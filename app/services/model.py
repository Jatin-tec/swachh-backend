import numpy as np
import pandas as pd

# Function to preprocess data and make predictions
def make_prediction(date_str, model, scaler_level, scaler_features):
    # Convert date and extract features
    date = pd.to_datetime(date_str, format='%d/%m/%Y')
    day_of_week = date.dayofweek
    month = date.month
    is_weekend = day_of_week >= 5

    # Example of rolling statistics and lag features (customize based on your data)
    rolling_mean = 0  # Replace with actual rolling mean calculation
    rolling_std = 0  # Replace with actual rolling std calculation
    level_lag_1 = 0  # Replace with actual lag calculation
    level_lag_2 = 0  # Replace with actual lag calculation

    # Normalize features (adjust according to your scalers)
    level = 0  # Replace with actual level value
    features = np.array([[level, day_of_week, month, is_weekend, rolling_mean, rolling_std, level_lag_1, level_lag_2]])

    # Apply scaling using respective scalers
    features[:, 0] = scaler_level.transform(features[:, 0].reshape(-1, 1)).flatten()
    features[:, 4:6] = scaler_features.transform(features[:, 4:6])  # Assuming rolling_mean and rolling_std are at index 4 and 5

    # Reshape features for LSTM input shape (samples, time steps, features)
    features = features.reshape((features.shape[0], 1, features.shape[1]))

    # Predict
    prediction = model.predict(features)
    prediction = scaler_level.inverse_transform(prediction)

    return prediction[0][0]