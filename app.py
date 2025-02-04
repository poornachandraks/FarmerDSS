from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from functools import wraps
from folium import Map, ClickForLatLng
import requests
from utils.weather import get_weather_data
import logging
import pickle
import numpy as np
import os
from joblib import load
import pandas as pd
from config import FLASK_SECRET_KEY

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY  # Using value from config

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('farmer_app.db')
        c = conn.cursor()
        
        user = c.execute('SELECT * FROM user_information WHERE Username = ?', 
                        (username,)).fetchone()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[2]
            session['role'] = user[4]
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
        
        conn.close()
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    
    try:
        highlighted_crop = request.args.get('highlight')
        
        # Fetch market trends with historical data
        market_trends = c.execute('''
            SELECT DISTINCT
                c.CropID,
                c.CropName,
                m.Region,
                m.Month,
                m.Year,
                m.AveragePrice
            FROM market_trends m 
            JOIN (
                SELECT MIN(CropID) as CropID, CropName
                FROM crop_information
                GROUP BY CropName
            ) c ON m.CropID = c.CropID 
            WHERE m.Year >= 2023
            ORDER BY c.CropName, m.Year DESC, m.Month DESC
        ''').fetchall()
        
        # Get unique crops for the dropdown
        unique_crops = c.execute('''
            SELECT DISTINCT c.CropID, c.CropName
            FROM (
                SELECT MIN(CropID) as CropID, CropName
                FROM crop_information
                GROUP BY CropName
            ) c
            JOIN market_trends m ON c.CropID = m.CropID
            ORDER BY c.CropName
        ''').fetchall()
        
        # Fetch crop information with fertilizer requirements
        crop_data = c.execute('''
            SELECT DISTINCT
                c.CropName,
                c.CropType,
                c.IdealSoilType,
                c.IdealTemperature,
                c.IdealHumidity,
                c.IdealPH,
                f.NitrogenReq || ' kg/acre N, ' || 
                f.PhosphorusReq || ' kg/acre P, ' || 
                f.PotassiumReq || ' kg/acre K' as Fertilizers
            FROM crop_information c
            LEFT JOIN fertilizer_requirements f ON c.CropID = f.CropID
            GROUP BY c.CropName
            ORDER BY c.CropName
        ''').fetchall()
        
        # Fetch active subsidies
        subsidies = c.execute('''
            SELECT DISTINCT
                c.CropName,
                s.SubsidyName,
                s.EligibilityCriteria,
                s.Amount
            FROM subsidy_information s
            JOIN (
                SELECT MIN(CropID) as CropID, CropName
                FROM crop_information
                GROUP BY CropName
            ) c ON s.CropID = c.CropID
            ORDER BY s.Amount DESC
        ''').fetchall()
        
        return render_template('dashboard.html', 
                             market_trends=market_trends,
                             unique_crops=unique_crops,
                             crop_data=crop_data,
                             subsidies=subsidies,
                             highlighted_crop=highlighted_crop)
                             
    except Exception as e:
        logging.error(f"Error in dashboard route: {e}")
        flash("An error occurred while fetching data")
        return redirect(url_for('login'))
        
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

# Load the model using joblib
try:
    model_path = 'model/crop_pred.pkl'  # Updated path to match your file
    logging.info(f"Attempting to load model from: {model_path}")
    
    # Check if file exists
    if not os.path.exists(model_path):
        logging.error(f"Model file not found at: {model_path}")
        model = None
    else:
        model = load(model_path)  # Use joblib to load
        logging.info(f"Loaded model type: {type(model)}")
        
        # Verify model has predict method
        if not hasattr(model, 'predict'):
            logging.error("Loaded object does not have predict method")
            model = None
            
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None

@app.route('/crop_prediction', methods=['GET'])
@login_required
def crop_prediction():
    return render_template('crop_prediction.html')

# Add this at the top of your file with other imports and constants
CROP_MAPPING = {
    0: "rice",
    1: "maize",
    2: "chickpea",
    3: "kidneybeans",
    4: "pigeonpeas",
    5: "mothbeans",
    6: "mungbean",
    7: "blackgram",
    8: "lentil",
    9: "pomegranate",
    10: "banana",
    11: "mango",
    12: "grapes",
    13: "watermelon",
    14: "muskmelon",
    15: "apple",
    16: "orange",
    17: "papaya",
    18: "coconut",
    19: "cotton",
    20: "jute",
    21: "coffee"
}

# Update the feature names to match exactly what the model expects
FEATURE_NAMES = [
    'Nitrogen', 'Phosphorus', 'Potassium', 
    'Temperature', 'Humidity', 'pH_Value'  # Changed 'ph' to 'pH_Value'
]

@app.route('/crop_prediction/predict', methods=['POST'])
@login_required
def predict():
    if model is None:
        return jsonify({
            'success': False,
            'message': 'Model not properly loaded'
        })
        
    try:
        # Get and validate form data
        try:
            nitrogen = float(request.form['nitrogen'])
            phosphorus = float(request.form['phosphorus'])
            potassium = float(request.form['potassium'])
            ph = float(request.form['ph'])
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            
            # Log raw input values
            logging.info(f"""
            Raw Input Values:
            - Nitrogen: {nitrogen}
            - Phosphorus: {phosphorus}
            - Potassium: {potassium}
            - pH: {ph}
            - Location: ({latitude}, {longitude})
            """)
            
            # Input validation with detailed ranges
            if not (0 <= nitrogen <= 140):
                raise ValueError(f"Nitrogen should be between 0 and 140, got {nitrogen}")
            if not (0 <= phosphorus <= 145):
                raise ValueError(f"Phosphorus should be between 0 and 145, got {phosphorus}")
            if not (0 <= potassium <= 205):
                raise ValueError(f"Potassium should be between 0 and 205, got {potassium}")
            if not (0 <= ph <= 14):
                raise ValueError(f"pH should be between 0 and 14, got {ph}")
                
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            })
        
        # Get weather data
        weather_data = get_weather_data(latitude=latitude, longitude=longitude)
        
        if not weather_data:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch weather data'
            })
        
        # Prepare input features with correct column names
        features = pd.DataFrame([[
            nitrogen, phosphorus, potassium,
            weather_data['temperature'],
            weather_data['humidity'],
            ph
        ]], columns=FEATURE_NAMES)
        
        # Make prediction
        try:
            prediction_result = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0] if hasattr(model, 'predict_proba') else None
            
            # Get top predictions
            significant_predictions = []
            if probabilities is not None:
                sorted_idx = np.argsort(probabilities)[::-1]
                for idx in sorted_idx:
                    prob = probabilities[idx]
                    if prob > 0.01:
                        crop = CROP_MAPPING.get(idx, 'unknown')
                        significant_predictions.append({
                            'crop': crop.title(),
                            'probability': float(prob)
                        })
                
            # Take top 3 predictions
            top_3_crops = significant_predictions[:3]
            
            # Save prediction to database
            conn = sqlite3.connect('farmer_app.db')
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO prediction_history 
                    (UserID, Nitrogen, Phosphorus, Potassium, Temperature, 
                     Humidity, pH, Location, PredictedCrop, Probability)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session['user_id'],
                    nitrogen,
                    phosphorus,
                    potassium,
                    weather_data['temperature'],
                    weather_data['humidity'],
                    ph,
                    f"{latitude}, {longitude}",
                    top_3_crops[0]['crop'],
                    top_3_crops[0]['probability']
                ))
                conn.commit()
            except Exception as e:
                logging.error(f"Error saving prediction: {e}")
                conn.rollback()
            finally:
                conn.close()
            
            # Prepare response
            response_data = {
                'success': True,
                'prediction': top_3_crops[0]['crop'],
                'weather': {
                    'region': str(weather_data['region']),
                    'temperature': float(weather_data['temperature']),
                    'humidity': float(weather_data['humidity']),
                    'rainfall': float(weather_data['rainfall'])
                },
                'top_predictions': top_3_crops
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            return jsonify({
                'success': False,
                'message': f'Error making prediction: {str(e)}'
            })
            
    except Exception as e:
        logging.error(f"Error in prediction route: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/update_weather')
@login_required
def update_weather():
    try:
        lat = float(request.args.get('lat', 28.6139))
        lon = float(request.args.get('lon', 77.2090))
        
        weather_data = get_weather_data(latitude=lat, longitude=lon)
        
        if weather_data:
            weather = [
                weather_data['region'],
                round(weather_data['temperature'], 1),
                round(weather_data['humidity'], 1),
                round(weather_data['rainfall'], 1)
            ]
            return jsonify({
                'success': True,
                'weather': weather,
                'coordinates': {
                    'lat': lat,
                    'lon': lon
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch weather data'
            })
            
    except Exception as e:
        logging.error(f"Error updating weather: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/get_crop_details/<crop_name>')
@login_required
def get_crop_details(crop_name):
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    
    try:
        # Fetch crop details including NPK requirements and ideal conditions
        crop_details = c.execute('''
            SELECT 
                c.IdealTemperature,
                c.IdealHumidity,
                c.IdealPH,
                f.NitrogenReq,
                f.PhosphorusReq,
                f.PotassiumReq
            FROM crop_information c
            LEFT JOIN fertilizer_requirements f ON c.CropID = f.CropID
            WHERE LOWER(c.CropName) = LOWER(?)
        ''', (crop_name,)).fetchone()
        
        if crop_details:
            return jsonify({
                'temperature': float(crop_details[0].replace('°C', '')),
                'humidity': float(crop_details[1].replace('%', '')),
                'ph': crop_details[2],
                'nitrogen': crop_details[3],
                'phosphorus': crop_details[4],
                'potassium': crop_details[5]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Crop details not found'
            })
            
    except Exception as e:
        logging.error(f"Error fetching crop details: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    finally:
        conn.close()

# Load crop data
df = pd.read_csv('data/Best_Values.csv')  # Updated path

# Database Management Routes

@app.route('/manage/crops', methods=['GET'])
@login_required
def manage_crops():
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        crops = c.execute('''
            SELECT DISTINCT
                c.CropID,
                c.CropName,
                c.CropType,
                c.IdealSoilType,
                c.IdealTemperature,
                c.IdealHumidity,
                c.IdealPH,
                f.NitrogenReq,
                f.PhosphorusReq,
                f.PotassiumReq
            FROM crop_information c
            LEFT JOIN fertilizer_requirements f ON c.CropID = f.CropID
            GROUP BY c.CropName
            ORDER BY c.CropName
        ''').fetchall()
        return render_template('manage/crops.html', crops=crops)
    except Exception as e:
        flash(f'Error fetching crops: {str(e)}')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

@app.route('/manage/crops/add', methods=['POST'])
@login_required
def add_crop():
    if session.get('role') != 'admin':
        flash('Only administrators can add crops')
        return redirect(url_for('manage_crops'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        # Extract form data
        crop_name = request.form['crop_name']
        crop_type = request.form['crop_type']
        soil_type = request.form['soil_type']
        temperature = request.form['temperature']
        humidity = request.form['humidity']
        ph = request.form['ph']
        nitrogen = request.form['nitrogen']
        phosphorus = request.form['phosphorus']
        potassium = request.form['potassium']
        
        # Insert into crop_information
        c.execute('''
            INSERT INTO crop_information 
            (CropName, CropType, IdealSoilType, IdealTemperature, IdealHumidity, IdealPH)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (crop_name, crop_type, soil_type, temperature, humidity, ph))
        
        crop_id = c.lastrowid
        
        # Insert into fertilizer_requirements
        c.execute('''
            INSERT INTO fertilizer_requirements 
            (CropID, NitrogenReq, PhosphorusReq, PotassiumReq)
            VALUES (?, ?, ?, ?)
        ''', (crop_id, nitrogen, phosphorus, potassium))
        
        conn.commit()
        flash('Crop added successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error adding crop: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_crops'))

@app.route('/manage/crops/edit/<int:crop_id>', methods=['POST'])
@login_required
def edit_crop(crop_id):
    if session.get('role') != 'admin':
        flash('Only administrators can edit crops')
        return redirect(url_for('manage_crops'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        # Extract form data
        crop_name = request.form['crop_name']
        crop_type = request.form['crop_type']
        soil_type = request.form['soil_type']
        temperature = request.form['temperature']
        humidity = request.form['humidity']
        ph = request.form['ph']
        nitrogen = request.form['nitrogen']
        phosphorus = request.form['phosphorus']
        potassium = request.form['potassium']
        
        # Update crop_information
        c.execute('''
            UPDATE crop_information 
            SET CropName=?, CropType=?, IdealSoilType=?, 
                IdealTemperature=?, IdealHumidity=?, IdealPH=?
            WHERE CropID=?
        ''', (crop_name, crop_type, soil_type, temperature, humidity, ph, crop_id))
        
        # Update fertilizer_requirements
        c.execute('''
            UPDATE fertilizer_requirements 
            SET NitrogenReq=?, PhosphorusReq=?, PotassiumReq=?
            WHERE CropID=?
        ''', (nitrogen, phosphorus, potassium, crop_id))
        
        conn.commit()
        flash('Crop updated successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating crop: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_crops'))

@app.route('/manage/crops/delete/<int:crop_id>', methods=['POST'])
@login_required
def delete_crop(crop_id):
    if session.get('role') != 'admin':
        flash('Only administrators can delete crops')
        return redirect(url_for('manage_crops'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        # Delete from fertilizer_requirements first (foreign key)
        c.execute('DELETE FROM fertilizer_requirements WHERE CropID = ?', (crop_id,))
        # Delete from crop_information
        c.execute('DELETE FROM crop_information WHERE CropID = ?', (crop_id,))
        conn.commit()
        flash('Crop deleted successfully')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting crop: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_crops'))

@app.route('/manage/subsidies', methods=['GET'])
@login_required
def manage_subsidies():
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        subsidies = c.execute('''
            SELECT DISTINCT
                s.SubsidyID,
                s.SubsidyName,
                s.EligibilityCriteria,
                s.Amount,
                c.CropName
            FROM subsidy_information s
            JOIN (
                SELECT MIN(CropID) as CropID, CropName
                FROM crop_information
                GROUP BY CropName
            ) c ON s.CropID = c.CropID
            ORDER BY s.Amount DESC
        ''').fetchall()
        
        # Get unique crops for the add subsidy form
        crops = c.execute('''
            SELECT MIN(CropID) as CropID, CropName 
            FROM crop_information 
            GROUP BY CropName 
            ORDER BY CropName
        ''').fetchall()
        
        return render_template('manage/subsidies.html', subsidies=subsidies, crops=crops)
    except Exception as e:
        flash(f'Error fetching subsidies: {str(e)}')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

@app.route('/manage/subsidies/add', methods=['POST'])
@login_required
def add_subsidy():
    if session.get('role') != 'admin':
        flash('Only administrators can add subsidies')
        return redirect(url_for('manage_subsidies'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        subsidy_name = request.form['subsidy_name']
        criteria = request.form['criteria']
        amount = float(request.form['amount'])
        crop_id = int(request.form['crop_id'])
        
        c.execute('''
            INSERT INTO subsidy_information 
            (SubsidyName, EligibilityCriteria, Amount, CropID)
            VALUES (?, ?, ?, ?)
        ''', (subsidy_name, criteria, amount, crop_id))
        
        conn.commit()
        flash('Subsidy added successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error adding subsidy: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_subsidies'))

@app.route('/manage/subsidies/edit/<int:subsidy_id>', methods=['POST'])
@login_required
def edit_subsidy(subsidy_id):
    if session.get('role') != 'admin':
        flash('Only administrators can edit subsidies')
        return redirect(url_for('manage_subsidies'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        subsidy_name = request.form['subsidy_name']
        criteria = request.form['criteria']
        amount = float(request.form['amount'])
        crop_id = int(request.form['crop_id'])
        
        c.execute('''
            UPDATE subsidy_information 
            SET SubsidyName=?, EligibilityCriteria=?, Amount=?, CropID=?
            WHERE SubsidyID=?
        ''', (subsidy_name, criteria, amount, crop_id, subsidy_id))
        
        conn.commit()
        flash('Subsidy updated successfully')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating subsidy: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_subsidies'))

@app.route('/manage/subsidies/delete/<int:subsidy_id>', methods=['POST'])
@login_required
def delete_subsidy(subsidy_id):
    if session.get('role') != 'admin':
        flash('Only administrators can delete subsidies')
        return redirect(url_for('manage_subsidies'))
        
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        c.execute('DELETE FROM subsidy_information WHERE SubsidyID = ?', (subsidy_id,))
        conn.commit()
        flash('Subsidy deleted successfully')
    except Exception as e:
        conn.rollback()
        flash(f'Error deleting subsidy: {str(e)}')
    finally:
        conn.close()
    return redirect(url_for('manage_subsidies'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        conn = sqlite3.connect('farmer_app.db')
        c = conn.cursor()
        
        try:
            # Check if username already exists
            existing_user = c.execute('SELECT * FROM user_information WHERE Username = ?', 
                                    (username,)).fetchone()
            if existing_user:
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
            
            # Create new farmer account
            hashed_password = generate_password_hash(password)
            c.execute('''
                INSERT INTO user_information (Name, Username, Password, Role, Region, PreferredCrops)
                VALUES (?, ?, ?, 'farmer', NULL, NULL)
            ''', (username, username, hashed_password))
            
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/prediction_history')
@login_required
def prediction_history():
    conn = sqlite3.connect('farmer_app.db')
    c = conn.cursor()
    try:
        # Fetch user's prediction history
        predictions = c.execute('''
            SELECT 
                PredictionID,
                Timestamp,
                Nitrogen,
                Phosphorus,
                Potassium,
                Temperature,
                Humidity,
                pH,
                Location,
                PredictedCrop,
                Probability
            FROM prediction_history
            WHERE UserID = ?
            ORDER BY Timestamp DESC
        ''', (session['user_id'],)).fetchall()
        
        return render_template('prediction_history.html', predictions=predictions)
    except Exception as e:
        flash(f'Error fetching prediction history: {str(e)}')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=8080) 