from database import db
from datetime import datetime

class Leave(db.Model):
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type = db.Column(db.String(50))  # sick, casual, annual, unpaid
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    days_count = db.Column(db.Integer, default=1)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'from_date': self.from_date.isoformat(),
            'to_date': self.to_date.isoformat(),
            'days_count': self.days_count,
            'reason': self.reason,
            'status': self.status,
            'approved_by': self.approved_by,
            'applied_on': self.applied_on.isoformat()
        }
