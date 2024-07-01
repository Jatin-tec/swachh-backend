import numpy as np
import pandas as pd

# Function to preprocess data and make predictions
def make_prediction(date_str, model, scaler_level, scaler_features, level, 
                    rolling_mean, rolling_std, level_lag_1, level_lag_2):
    # Convert date and extract features
    date = pd.to_datetime(date_str, format='%d/%m/%Y')
    day_of_week = date.dayofweek
    month = date.month
    is_weekend = day_of_week >= 5

    # Example data update logic
    # Update rolling statistics (with example logic, customize based on your data)
    rolling_mean = (rolling_mean * 6 + level) / 7
    rolling_std = np.std([rolling_mean, level])  # Simple example, update with actual calculation

    # Update lag features
    level_lag_2 = level_lag_1
    level_lag_1 = level

    # Normalize features (adjust according to your scalers)
    features = np.array([[level, day_of_week, month, is_weekend, rolling_mean, rolling_std, level_lag_1, level_lag_2]])

    # Apply scaling using respective scalers
    features[:, 0] = scaler_level.transform(features[:, 0].reshape(-1, 1)).flatten()
    features[:, 4:6] = scaler_features.transform(features[:, 4:6])  # Assuming rolling_mean and rolling_std are at index 4 and 5

    # Reshape features for LSTM input shape (samples, time steps, features)
    features = features.reshape((features.shape[0], 1, features.shape[1]))

    # Predict
    prediction = model.predict(features)
    prediction = scaler_level.inverse_transform(prediction)

    return prediction[0][0], rolling_mean, rolling_std, level_lag_1, level_lag_2
