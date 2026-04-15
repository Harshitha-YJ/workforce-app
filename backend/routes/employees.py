from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.employee import Employee
from database import db
from sqlalchemy import func

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    total = Employee.query.count()
    active = Employee.query.filter_by(status='active').count()
    by_dept = db.session.query(Employee.department, func.count(Employee.id)).group_by(Employee.department).all()
    return jsonify({'total': total, 'active': active, 'inactive': total - active,
        'by_department': [{'department': d, 'count': c} for d, c in by_dept]}), 200

@employees_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    return jsonify([e.to_dict() for e in Employee.query.all()]), 200

@employees_bp.route('/<int:emp_id>', methods=['GET'])
@jwt_required()
def get_employee(emp_id):
    return jsonify(Employee.query.get_or_404(emp_id).to_dict()), 200

@employees_bp.route('/', methods=['POST'])
@jwt_required()
def create_employee():
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 401
    data = request.get_json()
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'error': f"Email '{data['email']}' already exists."}), 400
    max_id = db.session.query(func.max(Employee.id)).scalar() or 0
    emp = Employee(employee_id=f"EMP{max_id+1:03d}", first_name=data['first_name'],
        last_name=data['last_name'], email=data['email'], phone=data.get('phone'),
        department=data.get('department'), designation=data.get('designation'),
        salary=data.get('salary', 0), status='active')
    db.session.add(emp)
    db.session.commit()
    return jsonify(emp.to_dict()), 201

@employees_bp.route('/<int:emp_id>', methods=['PUT'])
@jwt_required()
def update_employee(emp_id):
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 401
    emp = Employee.query.get_or_404(emp_id)
    data = request.get_json()
    for field in ['first_name','last_name','email','phone','department','designation','salary','status']:
        if field in data: setattr(emp, field, data[field])
    db.session.commit()
    return jsonify(emp.to_dict()), 200

@employees_bp.route('/<int:emp_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(emp_id):
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 401
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    return jsonify({'message': 'Employee deleted'}), 200

@employees_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def my_profile():
    """Employee sees their own profile"""
    from flask_jwt_extended import get_jwt_identity
    from models.user import User
    user = User.query.get(get_jwt_identity())
    if not user or not user.employee_id:
        return jsonify({'error': 'No employee profile linked to your account'}), 404
    emp = Employee.query.get(user.employee_id)
    if not emp:
        return jsonify({'error': 'Employee not found'}), 404
    return jsonify(emp.to_dict()), 200
