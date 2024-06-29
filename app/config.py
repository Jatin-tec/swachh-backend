import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://rootuser:rootpass@localhost:27017/ecocity?authSource=admin')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
