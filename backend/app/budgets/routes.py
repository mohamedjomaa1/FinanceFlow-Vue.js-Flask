from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app import mongo
from app.models import Budget
from app.utils.decorators import jwt_required_custom
from datetime import datetime
from bson import ObjectId

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/', methods=['POST'])
@jwt_required_custom
def create_budget():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate
        required = ['category', 'limit', 'month']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if budget already exists
        existing = mongo.db.budgets.find_one({
            'user_id': ObjectId(user_id),
            'category': data['category'],
            'month': data['month']
        })
        
        if existing:
            return jsonify({'error': 'Budget already exists for this category and month'}), 400
        
        # Create budget
        budget_data = Budget.create(data, user_id)
        result = mongo.db.budgets.insert_one(budget_data)
        
        budget = mongo.db.budgets.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Budget created successfully',
            'budget': Budget.to_json(budget)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_budgets():
    try:
        user_id = get_jwt_identity()
        month = request.args.get('month')  # Format: YYYY-MM
        
        query = {'user_id': ObjectId(user_id)}
        if month:
            query['month'] = month
        
        budgets = list(mongo.db.budgets.find(query))
        
        # Calculate spent amount for each budget
        result = []
        for budget in budgets:
            # Get spent amount
            start_date = datetime.strptime(budget['month'], '%Y-%m')
            if start_date.month == 12:
                end_date = datetime(start_date.year + 1, 1, 1)
            else:
                end_date = datetime(start_date.year, start_date.month + 1, 1)
            
            spent_pipeline = [
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'category': budget['category'],
                        'type': 'expense',
                        'date': {
                            '$gte': start_date,
                            '$lt': end_date
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total': {'$sum': '$amount'}
                    }
                }
            ]
            
            spent_result = list(mongo.db.transactions.aggregate(spent_pipeline))
            spent = spent_result[0]['total'] if spent_result else 0
            
            result.append(Budget.to_json(budget, spent))
        
        return jsonify({'budgets': result}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets_bp.route('/<budget_id>', methods=['GET'])
@jwt_required_custom
def get_budget(budget_id):
    try:
        user_id = get_jwt_identity()
        
        budget = mongo.db.budgets.find_one({
            '_id': ObjectId(budget_id),
            'user_id': ObjectId(user_id)
        })
        
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        
        # Calculate spent
        start_date = datetime.strptime(budget['month'], '%Y-%m')
        if start_date.month == 12:
            end_date = datetime(start_date.year + 1, 1, 1)
        else:
            end_date = datetime(start_date.year, start_date.month + 1, 1)
        
        spent_pipeline = [
            {
                '$match': {
                    'user_id': ObjectId(user_id),
                    'category': budget['category'],
                    'type': 'expense',
                    'date': {
                        '$gte': start_date,
                        '$lt': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': '$amount'}
                }
            }
        ]
        
        spent_result = list(mongo.db.transactions.aggregate(spent_pipeline))
        spent = spent_result[0]['total'] if spent_result else 0
        
        return jsonify({'budget': Budget.to_json(budget, spent)}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets_bp.route('/<budget_id>', methods=['PUT'])
@jwt_required_custom
def update_budget(budget_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check ownership
        budget = mongo.db.budgets.find_one({
            '_id': ObjectId(budget_id),
            'user_id': ObjectId(user_id)
        })
        
        if not budget:
            return jsonify({'error': 'Budget not found'}), 404
        
        # Prepare update
        update_data = {'updated_at': datetime.utcnow()}
        
        if 'limit' in data:
            update_data['limit'] = float(data['limit'])
        if 'category' in data:
            update_data['category'] = data['category']
        
        # Update
        mongo.db.budgets.update_one(
            {'_id': ObjectId(budget_id)},
            {'$set': update_data}
        )
        
        budget = mongo.db.budgets.find_one({'_id': ObjectId(budget_id)})
        
        # Calculate spent
        start_date = datetime.strptime(budget['month'], '%Y-%m')
        if start_date.month == 12:
            end_date = datetime(start_date.year + 1, 1, 1)
        else:
            end_date = datetime(start_date.year, start_date.month + 1, 1)
        
        spent_pipeline = [
            {
                '$match': {
                    'user_id': ObjectId(user_id),
                    'category': budget['category'],
                    'type': 'expense',
                    'date': {
                        '$gte': start_date,
                        '$lt': end_date
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': '$amount'}
                }
            }
        ]
        
        spent_result = list(mongo.db.transactions.aggregate(spent_pipeline))
        spent = spent_result[0]['total'] if spent_result else 0
        
        return jsonify({
            'message': 'Budget updated successfully',
            'budget': Budget.to_json(budget, spent)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets_bp.route('/<budget_id>', methods=['DELETE'])
@jwt_required_custom
def delete_budget(budget_id):
    try:
        user_id = get_jwt_identity()
        
        result = mongo.db.budgets.delete_one({
            '_id': ObjectId(budget_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Budget not found'}), 404
        
        return jsonify({'message': 'Budget deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budgets_bp.route('/overview', methods=['GET'])
@jwt_required_custom
def get_budget_overview():
    try:
        user_id = get_jwt_identity()
        month = request.args.get('month')  # Format: YYYY-MM
        
        if not month:
            # Use current month
            month = datetime.now().strftime('%Y-%m')
        
        # Get all budgets for the month
        budgets = list(mongo.db.budgets.find({
            'user_id': ObjectId(user_id),
            'month': month
        }))
        
        total_budget = 0
        total_spent = 0
        categories = []
        
        start_date = datetime.strptime(month, '%Y-%m')
        if start_date.month == 12:
            end_date = datetime(start_date.year + 1, 1, 1)
        else:
            end_date = datetime(start_date.year, start_date.month + 1, 1)
        
        for budget in budgets:
            total_budget += budget['limit']
            
            # Calculate spent
            spent_pipeline = [
                {
                    '$match': {
                        'user_id': ObjectId(user_id),
                        'category': budget['category'],
                        'type': 'expense',
                        'date': {
                            '$gte': start_date,
                            '$lt': end_date
                        }
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total': {'$sum': '$amount'}
                    }
                }
            ]
            
            spent_result = list(mongo.db.transactions.aggregate(spent_pipeline))
            spent = spent_result[0]['total'] if spent_result else 0
            total_spent += spent
            
            categories.append(Budget.to_json(budget, spent))
        
        return jsonify({
            'month': month,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'remaining': total_budget - total_spent,
            'percentage': (total_spent / total_budget * 100) if total_budget > 0 else 0,
            'categories': categories
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500