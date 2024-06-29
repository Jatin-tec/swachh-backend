from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_cors import CORS
from app.config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client.get_default_database()

    jwt.init_app(app)

    with app.app_context():
        from app.routes import auth, waste_management
        app.register_blueprint(auth.bp)
        app.register_blueprint(waste_management.bp)

    return app
