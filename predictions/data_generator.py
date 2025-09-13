import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from django.utils import timezone

def generate_synthetic_data(num_records=1000):
    """Generate synthetic emergency data for training"""
    np.random.seed(42)
    random.seed(42)
    
    # Define features
    data = {
        'timestamp': [],
        'temperature': [],
        'humidity': [],
        'air_quality': [],
        'wind_speed': [],
        'precipitation': [],
        'population_density': [],
        'building_density': [],
        'hour_of_day': [],
        'day_of_week': [],
        'is_holiday': [],
        'emergency_type': [],  # fire, accident, medical, natural_disaster, none
        'emergency_probability': []
    }
    
    # Generate time series data
    start_date = timezone.now() - timedelta(days=365)
    
    for i in range(num_records):
        # Timestamp
        time_delta = timedelta(hours=i)
        timestamp = start_date + time_delta
        data['timestamp'].append(timestamp)
        data['day_of_week'].append(timestamp.weekday())
        data['hour_of_day'].append(timestamp.hour)
        
        # Environmental factors
        data['temperature'].append(np.random.normal(25, 10))  # Celsius
        data['humidity'].append(np.random.normal(50, 20))     # Percentage
        data['air_quality'].append(np.random.normal(50, 20))  # AQI
        data['wind_speed'].append(np.random.exponential(5))   # km/h
        data['precipitation'].append(np.random.exponential(2)) # mm
        
        # Location factors
        data['population_density'].append(np.random.uniform(10, 1000))  # people/km²
        data['building_density'].append(np.random.uniform(0.1, 0.9))    # ratio
        
        # Holiday (randomly assign)
        data['is_holiday'].append(1 if random.random() < 0.05 else 0)
        
        # Determine emergency probability based on features
        temp_effect = max(0, data['temperature'][-1] - 30) / 20  # Higher temp increases risk
        wind_effect = data['wind_speed'][-1] / 20  # Higher wind increases risk
        humidity_effect = max(0, 30 - data['humidity'][-1]) / 30  # Lower humidity increases risk
        population_effect = data['population_density'][-1] / 500  # Higher density increases risk
        building_effect = data['building_density'][-1]  # Higher density increases risk
        holiday_effect = data['is_holiday'][-1] * 0.3  # Holidays slightly increase risk
        
        # Base probability with seasonal effect (higher in summer)
        is_summer = 5 <= timestamp.month <= 8
        base_prob = 0.01 + (0.02 if is_summer else 0)
        
        # Calculate final probability
        emergency_prob = base_prob + 0.2 * temp_effect + 0.1 * wind_effect + \
                        0.15 * humidity_effect + 0.2 * population_effect + \
                        0.15 * building_effect + holiday_effect
        
        # Cap probability
        emergency_prob = min(0.95, max(0.01, emergency_prob))
        data['emergency_probability'].append(emergency_prob)
        
        # Determine if emergency occurs based on probability
        if random.random() < emergency_prob:
            # Weight emergency types
            emergency_types = ['fire', 'accident', 'medical', 'natural_disaster']
            weights = [0.4, 0.3, 0.2, 0.1]
            data['emergency_type'].append(np.random.choice(emergency_types, p=weights))
        else:
            data['emergency_type'].append('none')
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some noise and outliers to simulate real data
    outlier_indices = np.random.choice(len(df), size=int(len(df)*0.01), replace=False)
    for idx in outlier_indices:
        df.loc[idx, 'temperature'] *= 1.5
        df.loc[idx, 'wind_speed'] *= 2
    
    # Save to CSV
    csv_path = 'ml_models/training_data/emergency_data.csv'
    df.to_csv(csv_path, index=False)
    print(f"Generated {num_records} synthetic records to {csv_path}")
    
    return df