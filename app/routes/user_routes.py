from flask import Blueprint, request, jsonify
from app.models.user import User, UserRole
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.routes.utils import role_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/admin', methods=['GET'])
@jwt_required()
@role_required(UserRole.ADMIN)
def admin_route():
    return jsonify({'message': 'Welcome, admin!'})

@user_bp.route('/user/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(UserRole.ADMIN)
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 204

@user_bp.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])

    if 'role' in data:
        new_user.role = data['role']

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@user_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Welcome {current_user["username"]}!'}), 200