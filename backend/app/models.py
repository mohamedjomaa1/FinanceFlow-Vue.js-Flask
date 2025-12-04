from datetime import datetime
from bson import ObjectId
import bcrypt

class User:
    @staticmethod
    def create(data):
        return {
            'email': data['email'],
            'password': bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()),
            'name': data.get('name', ''),
            'phone': data.get('phone', ''),
            'profile_picture': data.get('profile_picture', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
    
    @staticmethod
    def to_json(user):
        return {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', ''),
            'phone': user.get('phone', ''),
            'profile_picture': user.get('profile_picture', ''),
            'created_at': user['created_at'].isoformat()
        }

class Transaction:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': ObjectId(user_id),
            'amount': float(data['amount']),
            'category': data['category'],
            'type': data['type'],  # 'income' or 'expense'
            'description': data.get('description', ''),
            'date': datetime.fromisoformat(data['date'].replace('Z', '+00:00')),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def to_json(transaction):
        return {
            'id': str(transaction['_id']),
            'amount': transaction['amount'],
            'category': transaction['category'],
            'type': transaction['type'],
            'description': transaction.get('description', ''),
            'date': transaction['date'].isoformat(),
            'created_at': transaction['created_at'].isoformat()
        }

class Budget:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': ObjectId(user_id),
            'category': data['category'],
            'limit': float(data['limit']),
            'month': data['month'],  # Format: YYYY-MM
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    
    @staticmethod
    def to_json(budget, spent=0):
        return {
            'id': str(budget['_id']),
            'category': budget['category'],
            'limit': budget['limit'],
            'spent': spent,
            'remaining': budget['limit'] - spent,
            'percentage': (spent / budget['limit'] * 100) if budget['limit'] > 0 else 0,
            'month': budget['month']
        }

class PasswordReset:
    @staticmethod
    def create(user_id, token):
        return {
            'user_id': ObjectId(user_id),
            'token': token,
            'expires_at': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }