from flask import Blueprint, make_response
from flask_jwt_extended import jwt_required
from database import db
from io import BytesIO
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

reports_bp = Blueprint('reports', __name__)

# ── colour palette matching the app ──────────────────────────────────────────
PURPLE  = colors.HexColor('#6c63ff')
DARK    = colors.HexColor('#0a0a0f')
SURFACE = colors.HexColor('#13131a')
MUTED   = colors.HexColor('#6b6b80')
SUCCESS = colors.HexColor('#43e97b')
WARNING = colors.HexColor('#f9a825')
DANGER  = colors.HexColor('#ff6584')
WHITE   = colors.white
LIGHT   = colors.HexColor('#e8e8f0')
BORDER  = colors.HexColor('#2a2a3a')

def base_style():
    s = getSampleStyleSheet()
    return s

def build_pdf(title, subtitle, sections):
    """
    sections = list of (section_title, table_headers, table_rows, summary_text)
    Returns bytes of the PDF.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    s = base_style()

    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold',
        fontSize=22, textColor=PURPLE, spaceAfter=4, alignment=TA_LEFT)
    sub_style = ParagraphStyle('Sub', fontName='Helvetica',
        fontSize=10, textColor=MUTED, spaceAfter=2, alignment=TA_LEFT)
    section_style = ParagraphStyle('Section', fontName='Helvetica-Bold',
        fontSize=13, textColor=LIGHT, spaceBefore=18, spaceAfter=8)
    summary_style = ParagraphStyle('Summary', fontName='Helvetica',
        fontSize=9, textColor=MUTED, spaceBefore=4, spaceAfter=8)
    footer_style = ParagraphStyle('Footer', fontName='Helvetica',
        fontSize=8, textColor=MUTED, alignment=TA_RIGHT)

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("WorkForce", ParagraphStyle('Logo',
        fontName='Helvetica-Bold', fontSize=14, textColor=PURPLE, spaceAfter=2)))
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(subtitle, sub_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=PURPLE, spaceAfter=12))

    page_w = A4[0] - 3.6*cm   # usable width

    for section_title, headers, rows, summary in sections:
        story.append(Paragraph(section_title, section_style))

        if rows:
            col_count = len(headers)
            col_w = page_w / col_count

            table_data = [headers] + rows
            tbl = Table(table_data, colWidths=[col_w]*col_count, repeatRows=1)
            tbl.setStyle(TableStyle([
                # Header row
                ('BACKGROUND',    (0,0), (-1,0),  PURPLE),
                ('TEXTCOLOR',     (0,0), (-1,0),  WHITE),
                ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
                ('FONTSIZE',      (0,0), (-1,0),  9),
                ('ALIGN',         (0,0), (-1,0),  'CENTER'),
                ('TOPPADDING',    (0,0), (-1,0),  8),
                ('BOTTOMPADDING', (0,0), (-1,0),  8),
                # Data rows
                ('BACKGROUND',    (0,1), (-1,-1), SURFACE),
                ('TEXTCOLOR',     (0,1), (-1,-1), LIGHT),
                ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE',      (0,1), (-1,-1), 8),
                ('ALIGN',         (0,1), (-1,-1), 'CENTER'),
                ('TOPPADDING',    (0,1), (-1,-1), 6),
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                # Alternating rows
                *[('BACKGROUND', (0,i), (-1,i), colors.HexColor('#1a1a24'))
                  for i in range(2, len(table_data), 2)],
                # Grid
                ('GRID',          (0,0), (-1,-1), 0.4, BORDER),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [SURFACE, colors.HexColor('#1a1a24')]),
                ('ROUNDEDCORNERS', [4]),
            ]))
            story.append(tbl)
        else:
            story.append(Paragraph("No records found.", summary_style))

        if summary:
            story.append(Paragraph(summary, summary_style))

        story.append(Spacer(1, 8))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated on {date.today().strftime('%d %B %Y')}  ·  WorkForce Employee Management System  ·  Confidential",
        footer_style))

    doc.build(story)
    return buf.getvalue()


# ── Report routes ─────────────────────────────────────────────────────────────

@reports_bp.route('/employees', methods=['GET'])
@jwt_required()
def employee_report():
    from models.employee import Employee
    employees = Employee.query.order_by(Employee.department).all()

    headers = ['Emp ID', 'Full Name', 'Department', 'Designation', 'Salary (INR)', 'Status']
    rows = []
    for e in employees:
        rows.append([
            e.employee_id,
            f"{e.first_name} {e.last_name}",
            e.department or '—',
            e.designation or '—',
            f"Rs.{e.salary:,.0f}",
            e.status.upper()
        ])

    total_salary = sum(e.salary for e in employees)
    summary = (f"Total employees: {len(employees)}  ·  "
               f"Active: {sum(1 for e in employees if e.status=='active')}  ·  "
               f"Total payroll: Rs.{total_salary:,.0f}/month")

    pdf_bytes = build_pdf(
        title="Employee Directory Report",
        subtitle=f"All employees as of {date.today().strftime('%d %B %Y')}",
        sections=[("All Employees", headers, rows, summary)]
    )

    resp = make_response(pdf_bytes)
    resp.headers['Content-Type']        = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename="employee_report.pdf"'
    return resp


@reports_bp.route('/attendance', methods=['GET'])
@jwt_required()
def attendance_report():
    from models.attendance import Attendance
    from models.employee import Employee

    # Last 7 working days
    today = date.today()
    records = (Attendance.query
        .filter(Attendance.date >= today - timedelta(days=10))
        .order_by(Attendance.date.desc(), Attendance.employee_id)
        .all())

    emp_map = {e.id: e for e in Employee.query.all()}

    headers = ['Employee', 'Department', 'Date', 'Status', 'Check In', 'Check Out', 'Hours']
    rows = []
    for r in records:
        emp = emp_map.get(r.employee_id)
        name = f"{emp.first_name} {emp.last_name}" if emp else f"Emp #{r.employee_id}"
        dept = emp.department if emp else '—'
        rows.append([
            name, dept,
            r.date.strftime('%d %b %Y'),
            r.status.upper(),
            r.check_in.strftime('%H:%M') if r.check_in else '—',
            r.check_out.strftime('%H:%M') if r.check_out else '—',
            f"{r.hours_worked}h"
        ])

    present  = sum(1 for r in records if r.status == 'present')
    absent   = sum(1 for r in records if r.status == 'absent')
    late     = sum(1 for r in records if r.status == 'late')
    summary  = (f"Records shown: {len(records)}  ·  "
                f"Present: {present}  ·  Absent: {absent}  ·  Late: {late}")

    pdf_bytes = build_pdf(
        title="Attendance Report",
        subtitle=f"Last 10 days  ·  Generated {date.today().strftime('%d %B %Y')}",
        sections=[("Attendance Records", headers, rows, summary)]
    )

    resp = make_response(pdf_bytes)
    resp.headers['Content-Type']        = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
    return resp


@reports_bp.route('/leaves', methods=['GET'])
@jwt_required()
def leave_report():
    from models.leave import Leave
    from models.employee import Employee

    leaves = Leave.query.order_by(Leave.applied_on.desc()).all()
    emp_map = {e.id: e for e in Employee.query.all()}

    headers = ['Employee', 'Department', 'Type', 'From', 'To', 'Days', 'Status', 'Applied On']
    rows = []
    for l in leaves:
        emp = emp_map.get(l.employee_id)
        name = f"{emp.first_name} {emp.last_name}" if emp else f"Emp #{l.employee_id}"
        dept = emp.department if emp else '—'
        rows.append([
            name, dept,
            l.leave_type.title(),
            l.from_date.strftime('%d %b %Y'),
            l.to_date.strftime('%d %b %Y'),
            str(l.days_count),
            l.status.upper(),
            l.applied_on.strftime('%d %b %Y')
        ])

    pending  = sum(1 for l in leaves if l.status == 'pending')
    approved = sum(1 for l in leaves if l.status == 'approved')
    summary  = f"Total: {len(leaves)}  ·  Pending: {pending}  ·  Approved: {approved}"

    pdf_bytes = build_pdf(
        title="Leave Requests Report",
        subtitle=f"All leave applications  ·  Generated {date.today().strftime('%d %B %Y')}",
        sections=[("Leave Applications", headers, rows, summary)]
    )

    resp = make_response(pdf_bytes)
    resp.headers['Content-Type']        = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename="leave_report.pdf"'
    return resp
