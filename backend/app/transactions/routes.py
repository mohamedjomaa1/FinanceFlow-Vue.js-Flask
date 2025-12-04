from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import get_jwt_identity
from app import mongo
from app.models import Transaction
from app.utils.decorators import jwt_required_custom
from datetime import datetime
from bson import ObjectId
import csv
from io import StringIO

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/', methods=['POST'])
@jwt_required_custom
def create_transaction():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate
        required = ['amount', 'category', 'type', 'date']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if data['type'] not in ['income', 'expense']:
            return jsonify({'error': 'Type must be income or expense'}), 400
        
        # Create transaction
        transaction_data = Transaction.create(data, user_id)
        result = mongo.db.transactions.insert_one(transaction_data)
        
        transaction = mongo.db.transactions.find_one({'_id': result.inserted_id})
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': Transaction.to_json(transaction)
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_transactions():
    try:
        user_id = get_jwt_identity()
        
        # Query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category')
        type_ = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = {'user_id': ObjectId(user_id)}
        
        if category:
            query['category'] = category
        if type_:
            query['type'] = type_
        if start_date:
            query['date'] = {'$gte': datetime.fromisoformat(start_date.replace('Z', '+00:00'))}
        if end_date:
            if 'date' in query:
                query['date']['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                query['date'] = {'$lte': datetime.fromisoformat(end_date.replace('Z', '+00:00'))}
        
        # Get total count
        total = mongo.db.transactions.count_documents(query)
        
        # Get transactions
        transactions = list(mongo.db.transactions.find(query)
                          .sort('date', -1)
                          .skip((page - 1) * limit)
                          .limit(limit))
        
        return jsonify({
            'transactions': [Transaction.to_json(t) for t in transactions],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<transaction_id>', methods=['GET'])
@jwt_required_custom
def get_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        
        transaction = mongo.db.transactions.find_one({
            '_id': ObjectId(transaction_id),
            'user_id': ObjectId(user_id)
        })
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({'transaction': Transaction.to_json(transaction)}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<transaction_id>', methods=['PUT'])
@jwt_required_custom
def update_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check ownership
        transaction = mongo.db.transactions.find_one({
            '_id': ObjectId(transaction_id),
            'user_id': ObjectId(user_id)
        })
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Prepare update
        update_data = {'updated_at': datetime.utcnow()}
        
        if 'amount' in data:
            update_data['amount'] = float(data['amount'])
        if 'category' in data:
            update_data['category'] = data['category']
        if 'type' in data:
            if data['type'] not in ['income', 'expense']:
                return jsonify({'error': 'Invalid type'}), 400
            update_data['type'] = data['type']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'date' in data:
            update_data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        
        # Update
        mongo.db.transactions.update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': update_data}
        )
        
        transaction = mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': Transaction.to_json(transaction)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/<transaction_id>', methods=['DELETE'])
@jwt_required_custom
def delete_transaction(transaction_id):
    try:
        user_id = get_jwt_identity()
        
        result = mongo.db.transactions.delete_one({
            '_id': ObjectId(transaction_id),
            'user_id': ObjectId(user_id)
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/stats', methods=['GET'])
@jwt_required_custom
def get_stats():
    try:
        user_id = get_jwt_identity()
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = {'user_id': ObjectId(user_id)}
        
        if start_date:
            query['date'] = {'$gte': datetime.fromisoformat(start_date.replace('Z', '+00:00'))}
        if end_date:
            if 'date' in query:
                query['date']['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                query['date'] = {'$lte': datetime.fromisoformat(end_date.replace('Z', '+00:00'))}
        
        # Aggregate stats
        pipeline = [
            {'$match': query},
            {'$group': {
                '_id': '$type',
                'total': {'$sum': '$amount'}
            }}
        ]
        
        results = list(mongo.db.transactions.aggregate(pipeline))
        
        income = 0
        expenses = 0
        
        for r in results:
            if r['_id'] == 'income':
                income = r['total']
            elif r['_id'] == 'expense':
                expenses = r['total']
        
        # Category breakdown
        category_pipeline = [
            {'$match': {**query, 'type': 'expense'}},
            {'$group': {
                '_id': '$category',
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'total': -1}}
        ]
        
        categories = list(mongo.db.transactions.aggregate(category_pipeline))
        
        return jsonify({
            'income': income,
            'expenses': expenses,
            'balance': income - expenses,
            'categories': [{'category': c['_id'], 'amount': c['total']} for c in categories]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/export', methods=['GET'])
@jwt_required_custom
def export_transactions():
    try:
        user_id = get_jwt_identity()
        
        # Get filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        type_ = request.args.get('type')
        
        query = {'user_id': ObjectId(user_id)}
        
        if category:
            query['category'] = category
        if type_:
            query['type'] = type_
        if start_date:
            query['date'] = {'$gte': datetime.fromisoformat(start_date.replace('Z', '+00:00'))}
        if end_date:
            if 'date' in query:
                query['date']['$lte'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            else:
                query['date'] = {'$lte': datetime.fromisoformat(end_date.replace('Z', '+00:00'))}
        
        # Get transactions
        transactions = list(mongo.db.transactions.find(query).sort('date', -1))
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])
        
        # Write data
        for t in transactions:
            writer.writerow([
                t['date'].strftime('%Y-%m-%d'),
                t['type'],
                t['category'],
                t['amount'],
                t.get('description', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.csv'
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500