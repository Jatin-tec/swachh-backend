from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from flask_cors import CORS
from app.config import Config
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import pickle

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client.get_default_database()

    # Load the model architecture
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(1, 8)),
        Dense(1)
    ])

    # Load the model
    model.load_weights('app/utils/model/best_model.keras')
    app.model = model

    # Load the scaler
    with open('app/utils/model/scaler_level.pkl', 'rb') as f:
        app.scaler_level = pickle.load(f)

    with open('app/utils/model/scaler_features.pkl', 'rb') as f:
        app.scaler_features = pickle.load(f)

    jwt.init_app(app)

    with app.app_context():
        from app.routes import auth, waste_management
        app.register_blueprint(auth.bp)
        app.register_blueprint(waste_management.bp)

    return app
