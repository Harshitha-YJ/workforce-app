"""Run once to seed attendance demo data: python seed_attendance.py"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database import db
from models.attendance import Attendance
from models.employee import Employee
from datetime import date, timedelta, time
import random

app = create_app('development')

with app.app_context():
    employees = Employee.query.all()
    statuses = ['present', 'present', 'present', 'late', 'half-day', 'absent']

    for emp in employees:
        for days_ago in range(1, 8):  # Last 7 days
            d = date.today() - timedelta(days=days_ago)
            if d.weekday() >= 5:  # skip weekends
                continue
            if Attendance.query.filter_by(employee_id=emp.id, date=d).first():
                continue
            status = random.choice(statuses)
            rec = Attendance(
                employee_id=emp.id,
                date=d,
                status=status,
                check_in=time(9, random.randint(0, 30)) if status != 'absent' else None,
                check_out=time(18, random.randint(0, 30)) if status == 'present' else None,
                hours_worked=8 if status == 'present' else (4 if status == 'half-day' else 0)
            )
            db.session.add(rec)

    db.session.commit()
    print(f"✅ Seeded attendance for last 7 days for {len(employees)} employees")
