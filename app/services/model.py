import numpy as np
import pandas as pd

# Function to preprocess data and make predictions
def predict_future_bin_levels(current_level, current_date, num_days, model, scaler_level, scaler_features):
    future_levels = []
    current_date = pd.to_datetime(current_date)
    
    # Initial values
    rolling_mean = 0
    rolling_std = 0
    level_lag_1 = current_level
    level_lag_2 = current_level
    
    for _ in range(num_days):
        day_of_week = current_date.dayofweek
        month = current_date.month
        is_weekend = current_date.dayofweek >= 5
        
        # Create input feature array
        input_features = np.array([[
            current_level, day_of_week, month, is_weekend, rolling_mean, rolling_std, level_lag_1, level_lag_2
        ]])
        
        # Normalize features
        input_features[:, 0] = scaler_level.transform(input_features[:, 0].reshape(-1, 1)).reshape(-1)
        input_features[:, 4:6] = scaler_features.transform(input_features[:, 4:6])
        
        # Reshape for LSTM
        input_features = input_features.reshape((1, 1, input_features.shape[1]))
        
        # Predict the next bin level
        predicted_level = model.predict(input_features)
        predicted_level = scaler_level.inverse_transform(predicted_level).reshape(-1)[0]
        
        # Update rolling statistics and lags
        rolling_mean = (current_level + level_lag_1) / 2
        rolling_std = np.std([current_level, level_lag_1])
        level_lag_2 = level_lag_1
        level_lag_1 = current_level
        current_level = predicted_level
        current_date += pd.Timedelta(days=1)
        
        future_levels.append(predicted_level)
    
    return future_levels
