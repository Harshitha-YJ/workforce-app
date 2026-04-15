# WorkForce — Employee Management System

A full-stack Python (Flask) + JavaScript project built as an internship showcase.

## Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Auth:** JWT Tokens + Role-based access (Admin / Employee)

## Setup & Run

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000
Login: admin / admin123

## Project Structure
```
employee_mgmt/
├── backend/
│   ├── app.py              # Main Flask app
│   ├── config.py           # Config for dev/prod
│   ├── database.py         # DB + extension init
│   ├── models/             # SQLAlchemy models
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── attendance.py
│   │   └── leave.py
│   ├── routes/             # API blueprints
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── attendance.py
│   │   └── leave.py
│   └── requirements.txt
└── frontend/
    ├── templates/          # Jinja2 HTML templates
    │   ├── base.html
    │   ├── login.html
    │   ├── dashboard.html
    │   └── employees.html
    └── static/
        ├── css/
        └── js/
```

## API Endpoints (Day 1 & 2)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login | Login |
| GET | /api/auth/me | Get current user |
| GET | /api/employees/ | List all employees |
| POST | /api/employees/ | Add employee (admin) |
| PUT | /api/employees/:id | Update employee (admin) |
| DELETE | /api/employees/:id | Delete employee (admin) |
| GET | /api/employees/stats | Dashboard stats |
| GET | /api/attendance/ | Get attendance records |
| POST | /api/attendance/ | Mark attendance |
| GET | /api/leave/ | Get leave requests |
| POST | /api/leave/ | Apply for leave |
| PUT | /api/leave/:id/approve | Approve leave (admin) |
| PUT | /api/leave/:id/reject | Reject leave (admin) |
