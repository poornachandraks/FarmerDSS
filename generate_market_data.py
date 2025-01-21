import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Base prices with more variation
base_prices = {
    'rice': {'base': 2000, 'volatility': 0.15},
    'maize': {'base': 1800, 'volatility': 0.12},
    'chickpea': {'base': 4500, 'volatility': 0.18},
    'kidneybeans': {'base': 5000, 'volatility': 0.20},
    'pigeonpeas': {'base': 4800, 'volatility': 0.15},
    'mothbeans': {'base': 4600, 'volatility': 0.16},
    'mungbean': {'base': 4700, 'volatility': 0.17},
    'blackgram': {'base': 4800, 'volatility': 0.15},
    'lentil': {'base': 5200, 'volatility': 0.20},
    'pomegranate': {'base': 8000, 'volatility': 0.25},
    'banana': {'base': 3000, 'volatility': 0.20},
    'mango': {'base': 6000, 'volatility': 0.30},  # High volatility due to seasonality
    'grapes': {'base': 7000, 'volatility': 0.25},
    'watermelon': {'base': 2500, 'volatility': 0.35},  # Very seasonal
    'muskmelon': {'base': 3000, 'volatility': 0.35},
    'apple': {'base': 7500, 'volatility': 0.22},
    'orange': {'base': 4000, 'volatility': 0.20},
    'papaya': {'base': 3500, 'volatility': 0.18},
    'coconut': {'base': 2800, 'volatility': 0.15},
    'cotton': {'base': 6000, 'volatility': 0.25},
    'jute': {'base': 4500, 'volatility': 0.20},
    'coffee': {'base': 20000, 'volatility': 0.28}
}

# Generate market data
market_data = []
regions = ['North', 'South']
months = range(1, 13)
years = [2023, 2024]

for crop_name, price_info in base_prices.items():
    base_price = price_info['base']
    volatility = price_info['volatility']
    
    for region in regions:
        for year in years:
            for month in months[:6 if year == 2024 else 12]:  # Only first 6 months of 2024
                # Base seasonal effect (stronger for fruits and vegetables)
                seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (month - 3) / 12)  # Peak in summer
                
                # Regional variation
                regional_factor = 1.1 if region == 'North' else 0.9
                
                # Add random market shocks
                market_shock = np.random.normal(0, volatility)
                
                # Calculate final price
                price = base_price * (1 + market_shock) * seasonal_factor * regional_factor
                
                # Ensure price doesn't go below 50% or above 200% of base price
                price = max(base_price * 0.5, min(base_price * 2.0, price))
                
                market_data.append({
                    'CropID': list(base_prices.keys()).index(crop_name) + 1,
                    'Region': region,
                    'Month': month,
                    'Year': year,
                    'AveragePrice': round(price, 2)
                })

# Create DataFrame and save to CSV
df = pd.DataFrame(market_data)
df.to_csv('data/market_trends.csv', index=False)
print("Market trends data created successfully!") 