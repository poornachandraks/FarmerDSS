import sqlite3
from werkzeug.security import generate_password_hash
import random
import pandas as pd
import math

def init_db():
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    
    # Create User Information table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_information (
            UserID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Role TEXT NOT NULL,
            Region TEXT,
            PreferredCrops TEXT
        )
    ''')
    
    # Create Crop Information table
    c.execute('''
        CREATE TABLE IF NOT EXISTS crop_information (
            CropID INTEGER PRIMARY KEY AUTOINCREMENT,
            CropName TEXT NOT NULL,
            CropType TEXT,
            IdealSoilType TEXT,
            IdealTemperature REAL,
            IdealHumidity REAL,
            IdealPH REAL
        )
    ''')
    
    # Create Fertilizer Requirements table
    c.execute('''
        CREATE TABLE IF NOT EXISTS fertilizer_requirements (
            FertilizerID INTEGER PRIMARY KEY AUTOINCREMENT,
            CropID INTEGER,
            NitrogenReq REAL,
            PhosphorusReq REAL,
            PotassiumReq REAL,
            FOREIGN KEY (CropID) REFERENCES crop_information (CropID)
        )
    ''')
    
    # Create Market Trends table
    c.execute('''
        CREATE TABLE IF NOT EXISTS market_trends (
            MarketTrendID INTEGER PRIMARY KEY AUTOINCREMENT,
            CropID INTEGER,
            Region TEXT NOT NULL,
            Month INTEGER CHECK (Month >= 1 AND Month <= 12),
            Year INTEGER,
            AveragePrice FLOAT CHECK (AveragePrice > 0),
            FOREIGN KEY (CropID) REFERENCES crop_information (CropID)
        )
    ''')
    
    # Create Weather Data table
    c.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            WeatherID INTEGER PRIMARY KEY AUTOINCREMENT,
            Region TEXT NOT NULL,
            Month INTEGER CHECK (Month >= 1 AND Month <= 12),
            Year INTEGER,
            AverageRainfall FLOAT CHECK (AverageRainfall >= 0),
            AverageTemperature FLOAT
        )
    ''')
    
    # Create Subsidy Information table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subsidy_information (
            SubsidyID INTEGER PRIMARY KEY AUTOINCREMENT,
            CropID INTEGER,
            SubsidyName TEXT NOT NULL,
            EligibilityCriteria TEXT,
            Amount FLOAT,
            FOREIGN KEY (CropID) REFERENCES crop_information (CropID)
        )
    ''')
    
    # Insert a default admin user
    default_admin = ('Admin User', 'admin', 
                    generate_password_hash('admin123'), 
                    'admin', 'All', 'All')
    
    try:
        c.execute('''
            INSERT INTO user_information 
            (Name, Username, Password, Role, Region, PreferredCrops)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', default_admin)
    except sqlite3.IntegrityError:
        pass  # Admin user already exists
    
    # Insert sample crop data
    df = pd.read_csv('data/Best_Values.csv')

    for _, row in df.iterrows():
        try:
            c.execute('''
                INSERT INTO crop_information 
                (CropName, CropType, IdealSoilType, IdealTemperature, IdealHumidity, IdealPH)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row['Crop'],
                row['CropType'],
                row['IdealSoilType'],
                f"{row['Temperature']}°C",
                f"{row['Humidity']}%",
                row['pH_Value']
            ))
            
            # Get the CropID of the just inserted crop
            crop_id = c.lastrowid
            
            # Insert fertilizer requirements
            c.execute('''
                INSERT INTO fertilizer_requirements 
                (CropID, NitrogenReq, PhosphorusReq, PotassiumReq)
                VALUES (?, ?, ?, ?)
            ''', (
                crop_id,
                row['Nitrogen'],
                row['Phosphorus'],
                row['Potassium']
            ))
        except sqlite3.IntegrityError:
            pass  # Crop already exists
    
    # Insert market trends data from CSV
    market_trends_df = pd.read_csv('data/market_trends.csv')
    
    for _, row in market_trends_df.iterrows():
        try:
            c.execute('''
                INSERT INTO market_trends 
                (CropID, Region, Month, Year, AveragePrice)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['CropID'],
                row['Region'],
                row['Month'],
                row['Year'],
                row['AveragePrice']
            ))
        except sqlite3.IntegrityError:
            pass  # Skip if entry already exists
    
    # Insert sample weather data
    sample_weather = [
        ('North', 2024, 1100, 25),
        ('South', 2024, 1300, 28),
        ('East', 2024, 1500, 27),
        ('West', 2024, 900, 24),
        ('North', 2023, 1050, 26),
        ('South', 2023, 1250, 29),
        ('East', 2023, 1450, 28),
        ('West', 2023, 850, 25),
        ('North', 2022, 1000, 25),
        ('South', 2022, 1200, 28),
        ('East', 2022, 1400, 27),
        ('West', 2022, 800, 24)
    ]
    
    for weather in sample_weather:
        try:
            c.execute('''
                INSERT INTO weather_data 
                (Region, Year, AverageRainfall, AverageTemperature)
                VALUES (?, ?, ?, ?)
            ''', weather)
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample subsidy data
    sample_subsidies = [
        (1, 'Rice Support Scheme', 'Small Farmers', 5000),
        (1, 'Paddy Bonus Scheme', 'All Farmers', 2000),
        (2, 'Wheat Bonus', 'All Farmers', 3000),
        (2, 'Winter Crop Support', 'Marginal Farmers', 4000),
        (3, 'Cotton Price Support', 'Licensed Farmers', 7000),
        (4, 'Maize Development Scheme', 'Tribal Farmers', 3500),
        (5, 'Sugarcane Transport Subsidy', 'Registered Farmers', 6000),
        (6, 'Potato Cold Storage Scheme', 'Co-operative Members', 2500),
        (7, 'Vegetable Grower Support', 'Small Farmers', 1500),
        (8, 'Organic Farming Initiative', 'Certified Organic Farmers', 8000),
        (9, 'Oilseed Development Program', 'All Farmers', 4000),
        (10, 'Special Rabi Crop Scheme', 'Small & Marginal Farmers', 3000)
    ]
    
    for subsidy in sample_subsidies:
        try:
            c.execute('''
                INSERT INTO subsidy_information 
                (CropID, SubsidyName, EligibilityCriteria, Amount)
                VALUES (?, ?, ?, ?)
            ''', subsidy)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db() 