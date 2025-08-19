from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    # app.config['JWT_SECRET_KEY'] = 'secret_key'
    app.config.from_object(Config)
    
    jwt.init_app(app)
    db.init_app(app)
    
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    return app