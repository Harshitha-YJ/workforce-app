from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.leave import Leave
from database import db
from datetime import date

leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/', methods=['GET'])
@jwt_required()
def get_leaves():
    status = request.args.get('status')
    emp_id = request.args.get('employee_id')
    query = Leave.query
    if status: query = query.filter_by(status=status)
    if emp_id: query = query.filter_by(employee_id=emp_id)
    return jsonify([l.to_dict() for l in query.order_by(Leave.applied_on.desc()).all()]), 200

@leave_bp.route('/', methods=['POST'])
@jwt_required()
def apply_leave():
    data = request.get_json()
    from_date = date.fromisoformat(data['from_date'])
    to_date = date.fromisoformat(data['to_date'])
    leave = Leave(employee_id=data['employee_id'], leave_type=data.get('leave_type', 'casual'),
        from_date=from_date, to_date=to_date, days_count=(to_date - from_date).days + 1,
        reason=data.get('reason', ''), status='pending')
    db.session.add(leave)
    db.session.commit()
    return jsonify(leave.to_dict()), 201

@leave_bp.route('/<int:leave_id>/approve', methods=['PUT'])
@jwt_required()
def approve_leave(leave_id):
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 401
    leave = Leave.query.get_or_404(leave_id)
    leave.status = 'approved'
    leave.approved_by = get_jwt_identity()
    db.session.commit()
    return jsonify(leave.to_dict()), 200

@leave_bp.route('/<int:leave_id>/reject', methods=['PUT'])
@jwt_required()
def reject_leave(leave_id):
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 401
    leave = Leave.query.get_or_404(leave_id)
    leave.status = 'rejected'
    leave.approved_by = get_jwt_identity()
    db.session.commit()
    return jsonify(leave.to_dict()), 200

@leave_bp.route('/my-leaves', methods=['GET'])
@jwt_required()
def my_leaves():
    """Employee sees only their own leave requests"""
    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    user = User.query.get(get_jwt_identity())
    if not user or not user.employee_id:
        return jsonify({'error': 'No employee profile linked'}), 404
    leaves = Leave.query.filter_by(employee_id=user.employee_id)\
        .order_by(Leave.applied_on.desc()).all()
    return jsonify([l.to_dict() for l in leaves]), 200

@leave_bp.route('/my-apply', methods=['POST'])
@jwt_required()
def my_apply_leave():
    """Employee applies leave for themselves"""
    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    user = User.query.get(get_jwt_identity())
    if not user or not user.employee_id:
        return jsonify({'error': 'No employee profile linked'}), 404
    data = request.get_json()
    from_date = date.fromisoformat(data['from_date'])
    to_date   = date.fromisoformat(data['to_date'])
    leave = Leave(
        employee_id=user.employee_id,
        leave_type=data.get('leave_type', 'casual'),
        from_date=from_date, to_date=to_date,
        days_count=(to_date - from_date).days + 1,
        reason=data.get('reason', ''), status='pending'
    )
    db.session.add(leave)
    db.session.commit()
    return jsonify(leave.to_dict()), 201
