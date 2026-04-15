import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template
from config import config
from database import db, bcrypt, jwt, cors

def create_app(config_name='default'):
    app = Flask(
        __name__,
        static_folder='../frontend/static',
        template_folder='../frontend/templates'
    )

    app.config.from_object(config[config_name])

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from routes.auth import auth_bp
    from routes.employees import employees_bp
    from routes.attendance import attendance_bp
    from routes.leave import leave_bp
    from routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(leave_bp, url_prefix='/api/leave')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/signup')
    def signup():
        return render_template('signup.html')

    @app.route('/employee-dashboard')
    def employee_dashboard():
        return render_template('employee_dashboard.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/employees')
    def employees():
        return render_template('employees.html')

    @app.route('/attendance')
    def attendance():
        return render_template('attendance.html')

    @app.route('/leave')
    def leave():
        return render_template('leave.html')

    @app.route('/reports')
    def reports():
        return render_template('reports.html')

    with app.app_context():
        db.create_all()
        seed_data(app)
        seed_attendance(app)

    return app

def seed_data(app):
    from models.user import User
    from models.employee import Employee

    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@company.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        sample_employees = [
            ('Arjun',  'Sharma', 'arjun@company.com',  'Engineering', 'Backend Developer',      75000),
            ('Priya',  'Patel',  'priya@company.com',  'Design',      'UI/UX Designer',          65000),
            ('Rohit',  'Kumar',  'rohit@company.com',  'Engineering', 'Frontend Developer',      70000),
            ('Sneha',  'Reddy',  'sneha@company.com',  'HR',          'HR Manager',              60000),
            ('Vikram', 'Singh',  'vikram@company.com', 'Engineering', 'Full Stack Developer',    80000),
        ]

        for i, (fn, ln, email, dept, desig, sal) in enumerate(sample_employees, 1):
            emp = Employee(
                employee_id=f'EMP{i:03d}',
                first_name=fn, last_name=ln,
                email=email, department=dept,
                designation=desig, salary=sal,
                status='active'
            )
            db.session.add(emp)

        db.session.commit()

        from models.attendance import Attendance as Att
        from datetime import date, timedelta, time as t
        import random
        statuses = ['present', 'present', 'present', 'late', 'present', 'half-day', 'absent']
        employees = Employee.query.all()
        for emp in employees:
            for days_ago in range(7, 0, -1):
                att_date = date.today() - timedelta(days=days_ago)
                if att_date.weekday() >= 5:
                    continue
                status = random.choice(statuses)
                check_in  = t(9 if status != 'late' else 10, random.randint(0, 59))
                check_out = t(18, random.randint(0, 59))
                hours = round((check_out.hour*60 + check_out.minute - check_in.hour*60 - check_in.minute) / 60, 1)
                att = Att(
                    employee_id=emp.id, date=att_date,
                    status=status, check_in=check_in, check_out=check_out,
                    hours_worked=hours if status != 'absent' else 0
                )
                db.session.add(att)
        try:
            db.session.commit()
            print("✅ Seed data created — admin:admin123")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Seed skipped: {e}")

def seed_attendance(app):
    from models.attendance import Attendance
    from models.employee import Employee
    from datetime import date, timedelta, time
    import random
    with app.app_context():
        employees = Employee.query.all()
        statuses = ["present","present","present","late","half-day","absent"]
        for emp in employees:
            for days_ago in range(1, 8):
                d = date.today() - timedelta(days=days_ago)
                if d.weekday() >= 5: continue
                if Attendance.query.filter_by(employee_id=emp.id, date=d).first(): continue
                status = random.choice(statuses)
                rec = Attendance(
                    employee_id=emp.id, date=d, status=status,
                    check_in=time(9, random.randint(0,30)) if status != "absent" else None,
                    check_out=time(18, random.randint(0,30)) if status == "present" else None,
                    hours_worked=8 if status=="present" else (4 if status=="half-day" else 0)
                )
                db.session.add(rec)
        db.session.commit()
        print("✅ Attendance seeded")

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, port=5000)
