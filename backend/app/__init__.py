from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .config import Config

mongo = PyMongo()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    mongo.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.transactions.routes import transactions_bp
    from app.budgets.routes import budgets_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(budgets_bp, url_prefix='/api/budgets')
    
    # Create indexes
    with app.app_context():
        mongo.db.users.create_index('email', unique=True)
        mongo.db.transactions.create_index([('user_id', 1), ('date', -1)])
        mongo.db.budgets.create_index([('user_id', 1), ('category', 1)])
        mongo.db.password_resets.create_index('expires_at', expireAfterSeconds=0)
    
    return app