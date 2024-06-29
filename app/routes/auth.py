from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    if app.db.users.find_one({'email': email}):
        return jsonify({'msg': 'User already exists'}), 400

    try:
        user = {
            'email': email, 
            'password': password,
            'role': 'user',
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'last_login': datetime.now()
        }
        app.db.users.insert_one(user)
        access_token = create_access_token(identity=email)

        return jsonify({
            'email': email,
            'role': 'user',
            'status': 'active',
            'last_login': user['last_login'].strftime('%Y-%m-%d %H:%M:%S'),
            'access_token': access_token
            }), 200
    except:
        return jsonify({'msg': 'Internal server error'}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'msg': 'Email and password are required'}), 400

    try:
        user = app.db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'msg': 'Invalid credentials'}), 401

        app.db.users.update_one({'email': email}, {'$set': {'last_login': datetime.now()}})

        access_token = create_access_token(identity=email)
        return jsonify({
            'email': user['email'],
            'role': user['role'],
            'status': user['status'],
            'last_login': user['last_login'].strftime('%Y-%m-%d %H:%M:%S'),
            'access_token': access_token
            }), 200
    except:
        return jsonify({'msg': 'Internal server error'}), 500