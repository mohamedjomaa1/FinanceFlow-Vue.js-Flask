from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from app import mongo
from app.models import User, PasswordReset
from app.utils.decorators import jwt_required_custom
from app.utils.email import send_password_reset_email, send_sms, generate_reset_token
from datetime import datetime, timedelta
from bson import ObjectId
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Check if user exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_data = User.create(data)
        result = mongo.db.users.insert_one(user_data)
        
        # Generate tokens
        access_token = create_access_token(identity=str(result.inserted_id))
        refresh_token = create_refresh_token(identity=str(result.inserted_id))
        
        user = mongo.db.users.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': User.to_json(user)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = mongo.db.users.find_one({'email': data['email']})
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not User.verify_password(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=str(user['_id']))
        refresh_token = create_refresh_token(identity=str(user['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': User.to_json(user)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required_custom
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': User.to_json(user)}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow()
        }
        
        if 'name' in data:
            update_data['name'] = data['name']
        if 'phone' in data:
            update_data['phone'] = data['phone']
        if 'profile_picture' in data:
            update_data['profile_picture'] = data['profile_picture']
        
        # Update user
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': User.to_json(user)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        method = data.get('method', 'email')  # 'email' or 'sms'
        
        if method == 'email':
            email = data.get('email')
            if not email:
                return jsonify({'error': 'Email is required'}), 400
            
            user = mongo.db.users.find_one({'email': email})
            if not user:
                return jsonify({'message': 'If email exists, reset link sent'}), 200
            
            # Generate token
            token = generate_reset_token()
            
            # Store token
            reset_data = PasswordReset.create(user['_id'], token)
            reset_data['expires_at'] = datetime.utcnow() + timedelta(hours=1)
            mongo.db.password_resets.insert_one(reset_data)
            
            # Send email
            send_password_reset_email(email, token)
            
            return jsonify({'message': 'Password reset link sent to email'}), 200
        
        elif method == 'sms':
            phone = data.get('phone')
            if not phone:
                return jsonify({'error': 'Phone number is required'}), 400
            
            user = mongo.db.users.find_one({'phone': phone})
            if not user:
                return jsonify({'message': 'If phone exists, reset code sent'}), 200
            
            # Generate token
            token = generate_reset_token()
            
            # Store token
            reset_data = PasswordReset.create(user['_id'], token)
            reset_data['expires_at'] = datetime.utcnow() + timedelta(hours=1)
            mongo.db.password_resets.insert_one(reset_data)
            
            # Send SMS
            message = f"Your FinanceFlow password reset code: {token[:8]}"
            send_sms(phone, message)
            
            return jsonify({'message': 'Password reset code sent via SMS'}), 200
        
        else:
            return jsonify({'error': 'Invalid method'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and password are required'}), 400
        
        # Find valid token
        reset = mongo.db.password_resets.find_one({
            'token': token,
            'expires_at': {'$gt': datetime.utcnow()}
        })
        
        if not reset:
            return jsonify({'error': 'Invalid or expired token'}), 400
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        mongo.db.users.update_one(
            {'_id': reset['user_id']},
            {'$set': {
                'password': hashed_password,
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Delete reset token
        mongo.db.password_resets.delete_one({'_id': reset['_id']})
        
        return jsonify({'message': 'Password reset successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required_custom
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password are required'}), 400
        
        # Get user
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        
        # Verify current password
        if not User.verify_password(user['password'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'password': hashed_password,
                'updated_at': datetime.utcnow()
            }}
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500