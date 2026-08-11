import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import scipy.stats as stats
import statsmodels.api as sm
from services.matlab_service import run_fft

def process_sensor_data(df: pd.DataFrame, equipment_type: str) -> dict:
    """
    Cleanses data, calculates dynamic thresholds, detects anomalies, and extracts features.
    """
    # 1. Data Cleansing: Interpolate missing values (Garbage Data handling)
    # Assuming standard format: first column is Date/Time, others are sensor values
    time_col = df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col]).sort_values(by=time_col)
    
    # Interpolate numerical columns
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
    
    # 2. MATLAB Signal Processing (Optional/Conditional)
    # If high-frequency data, we might run FFT. We'll pass the first numerical column as an example.
    # In a real scenario, this would depend on the sensor type (e.g., vibration).
    fft_results = {}
    try:
        if len(num_cols) > 0:
            main_signal = df[num_cols[0]].values.tolist()
            fft_results = run_fft(main_signal)
    except Exception as e:
        print(f"MATLAB Engine Error or not configured: {e}")
    
    # 3. Anomaly Detection (FDC)
    # We use Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.05, random_state=42)
    # Fit model on the numerical features
    df['anomaly_score'] = model.fit_predict(df[num_cols])
    
    # Map -1 to True (Anomaly) and 1 to False (Normal)
    df['is_anomaly'] = df['anomaly_score'] == -1
    
    # 4. Adaptive Threshold (Moving Average)
    # Calculate moving average to simulate baseline shift due to aging
    window_size = min(50, len(df))
    for col in num_cols:
        df[f'{col}_ma'] = df[col].rolling(window=window_size, min_periods=1).mean()
        # Define upper control limit (e.g., MA + 3 * std)
        rolling_std = df[col].rolling(window=window_size, min_periods=1).std().fillna(0)
        df[f'{col}_ucl'] = df[f'{col}_ma'] + (3 * rolling_std)
        # Mark anomalies based on moving threshold as an additional check
        df[f'{col}_ma_anomaly'] = df[col] > df[f'{col}_ucl']
        
        # Combine anomalies
        df['is_anomaly'] = df['is_anomaly'] | df[f'{col}_ma_anomaly']

    # 5. Extract Keywords from Anomalies
    anomaly_keywords = []
    if df['is_anomaly'].any():
        # Identify which columns contributed most to the anomaly
        anomaly_rows = df[df['is_anomaly']]
        for col in num_cols:
            if anomaly_rows[f'{col}_ma_anomaly'].any():
                anomaly_keywords.append(f"High {col}")
        anomaly_keywords.append("Abnormal Vibration/Temperature") # Generic keyword
    
    # Return processed data for frontend consumption
    # Convert datetime to string for JSON serialization
    df[time_col] = df[time_col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        "chart_data": df.to_dict(orient='records'),
        "has_anomaly": bool(df['is_anomaly'].any()),
        "anomaly_keywords": list(set(anomaly_keywords)),
        "fft_summary": fft_results
    }
