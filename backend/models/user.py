from database import db, bcrypt
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80), unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(255), nullable=False)
    role         = db.Column(db.String(20), default='employee')   # 'admin' or 'employee'
    employee_id  = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    is_active    = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
