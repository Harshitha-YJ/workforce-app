from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.user import User
from models.employee import Employee
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not user.check_password(data.get('password')):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({'token': token, 'user': user.to_dict()}), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Public signup — employee enters their company email to self-register"""
    data = request.get_json()
    username  = data.get('username', '').strip()
    email     = data.get('email', '').strip()
    password  = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Try to link to an existing employee record by email
    employee = Employee.query.filter_by(email=email).first()

    user = User(
        username=username,
        email=email,
        role='employee',
        employee_id=employee.id if employee else None
    )
    user.set_password(password)
    db.session.add(user)

    # Also update the employee record to link back
    if employee:
        employee.user_id = None  # will be set after commit when we get user.id
    db.session.commit()

    if employee:
        employee.user_id = user.id
        db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'linked_employee': employee.to_dict() if employee else None
    }), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get(get_jwt_identity())
    if not user:
        return jsonify({'error': 'User not found'}), 404
    result = user.to_dict()
    # Attach employee info if linked
    if user.employee_id:
        emp = Employee.query.get(user.employee_id)
        if emp:
            result['employee'] = emp.to_dict()
    return jsonify(result), 200

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Admin-only: create a user and link to employee"""
    if get_jwt().get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    user = User(username=data['username'], email=data['email'], role=data.get('role', 'employee'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
