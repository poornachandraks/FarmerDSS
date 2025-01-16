from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key

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
        # Fetch latest weather data
        weather_data = c.execute('''
            SELECT Region, AverageTemperature, AverageRainfall 
            FROM weather_data 
            WHERE Year = 2024 AND Month = (
                SELECT MAX(Month) FROM weather_data WHERE Year = 2024
            )
            LIMIT 1
        ''').fetchone()
        
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
            JOIN crop_information c ON m.CropID = c.CropID 
            WHERE m.Year >= 2023
            ORDER BY c.CropName, m.Year DESC, m.Month DESC
        ''').fetchall()
        
        # Get unique crops for the dropdown
        unique_crops = c.execute('''
            SELECT DISTINCT c.CropID, c.CropName
            FROM crop_information c
            JOIN market_trends m ON c.CropID = m.CropID
            ORDER BY c.CropName
        ''').fetchall()
        
        # Fetch crop information with fertilizer requirements
        crop_data = c.execute('''
            SELECT 
                c.CropName,
                c.CropType,
                c.IdealSoilType,
                c.WaterRequirement,
                GROUP_CONCAT(f.FertilizerName || ' (' || f.QuantityPerAcre || ' kg/acre)') as Fertilizers
            FROM crop_information c
            LEFT JOIN fertilizer_requirements f ON c.CropID = f.CropID
            GROUP BY c.CropID
            ORDER BY c.CropName
        ''').fetchall()
        
        # Fetch active subsidies
        subsidies = c.execute('''
            SELECT 
                c.CropName,
                s.SubsidyName,
                s.EligibilityCriteria,
                s.Amount
            FROM subsidy_information s
            JOIN crop_information c ON s.CropID = c.CropID
            ORDER BY s.Amount DESC
        ''').fetchall()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash("An error occurred while fetching data")
        return redirect(url_for('login'))
        
    finally:
        conn.close()
    
    return render_template('dashboard.html', 
                         weather=weather_data,
                         market_trends=market_trends,
                         unique_crops=unique_crops,
                         crop_data=crop_data,
                         subsidies=subsidies)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Changed to port 8080 