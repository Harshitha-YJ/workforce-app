from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.attendance import Attendance
from models.employee import Employee
from database import db
from datetime import date, datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/', methods=['GET'])
@jwt_required()
def get_attendance():
    emp_id = request.args.get('employee_id')
    status  = request.args.get('status')
    date_str = request.args.get('date')

    query = Attendance.query
    if emp_id:
        query = query.filter_by(employee_id=int(emp_id))
    if status:
        query = query.filter_by(status=status)
    if date_str:
        try:
            query = query.filter_by(date=date.fromisoformat(date_str))
        except ValueError:
            pass

    records = query.order_by(Attendance.date.desc()).limit(200).all()
    return jsonify([r.to_dict() for r in records]), 200

@attendance_bp.route('/', methods=['POST'])
@jwt_required()
def mark_attendance():
    data = request.get_json()
    existing = Attendance.query.filter_by(
        employee_id=data['employee_id'],
        date=date.fromisoformat(data['date'])
    ).first()
    if existing:
        return jsonify({'error': 'Attendance already marked for this date'}), 400

    record = Attendance(
        employee_id=data['employee_id'],
        date=date.fromisoformat(data['date']),
        status=data.get('status', 'present'),
        check_in=datetime.strptime(data['check_in'], '%H:%M').time() if data.get('check_in') else None,
        check_out=datetime.strptime(data['check_out'], '%H:%M').time() if data.get('check_out') else None,
        hours_worked=data.get('hours_worked', 0),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201

@attendance_bp.route('/summary', methods=['GET'])
@jwt_required()
def summary():
    employees = Employee.query.filter_by(status='active').all()
    today = date.today()
    result = []
    for emp in employees:
        att = Attendance.query.filter_by(employee_id=emp.id, date=today).first()
        result.append({
            'employee': emp.to_dict(),
            'today': att.to_dict() if att else None
        })
    return jsonify(result), 200

@attendance_bp.route('/chart-data', methods=['GET'])
@jwt_required()
def chart_data():
    """Returns last 7 days attendance counts grouped by status for charts"""
    from models.employee import Employee
    from datetime import date, timedelta
    from sqlalchemy import func

    today = date.today()
    result = []
    for days_ago in range(6, -1, -1):
        d = today - timedelta(days=days_ago)
        if d.weekday() >= 5:
            continue
        day_label = d.strftime('%a %d')
        counts = dict(db.session.query(Attendance.status, func.count(Attendance.id))
            .filter(Attendance.date == d).group_by(Attendance.status).all())
        result.append({
            'date': day_label,
            'present':  counts.get('present', 0),
            'absent':   counts.get('absent', 0),
            'late':     counts.get('late', 0),
            'half_day': counts.get('half-day', 0),
        })
    return jsonify(result), 200

@attendance_bp.route('/my-attendance', methods=['GET'])
@jwt_required()
def my_attendance():
    """Employee sees only their own attendance"""
    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    user = User.query.get(get_jwt_identity())
    if not user or not user.employee_id:
        return jsonify({'error': 'No employee profile linked'}), 404
    records = Attendance.query.filter_by(employee_id=user.employee_id)\
        .order_by(Attendance.date.desc()).limit(30).all()
    return jsonify([r.to_dict() for r in records]), 200

@attendance_bp.route('/my-stats', methods=['GET'])
@jwt_required()
def my_stats():
    """Attendance summary stats for the logged-in employee"""
    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    from sqlalchemy import func
    user = User.query.get(get_jwt_identity())
    if not user or not user.employee_id:
        return jsonify({'error': 'No employee profile linked'}), 404
    counts = dict(db.session.query(Attendance.status, func.count(Attendance.id))
        .filter(Attendance.employee_id == user.employee_id)
        .group_by(Attendance.status).all())
    total_hours = db.session.query(func.sum(Attendance.hours_worked))\
        .filter(Attendance.employee_id == user.employee_id).scalar() or 0
    return jsonify({
        'present':  counts.get('present', 0),
        'absent':   counts.get('absent', 0),
        'late':     counts.get('late', 0),
        'half_day': counts.get('half-day', 0),
        'total_hours': round(total_hours, 1)
    }), 200
