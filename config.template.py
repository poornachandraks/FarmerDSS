from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys and Secrets (loaded from .env)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///farmerdss.db')

# Basic validation limits
SOIL_PARAMS_LIMITS = {
    'nitrogen': {'min': 0, 'max': 140},
    'phosphorus': {'min': 0, 'max': 145},
    'potassium': {'min': 0, 'max': 205},
    'ph': {'min': 0, 'max': 14}
}

# API Rate Limiting
API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '100'))  # requests per hour
API_RATE_LIMIT_WINDOW = int(os.getenv('API_RATE_LIMIT_WINDOW', '3600'))  # in seconds

# Security Settings
CSRF_ENABLED = True
SSL_ENABLED = os.getenv('SSL_ENABLED', 'False').lower() == 'true'

# Weather API Configuration
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5"
WEATHER_API_GEOCODING_URL = "https://api.openweathermap.org/geo/1.0"
WEATHER_UNITS = "metric"

# Cache Configuration
CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

# Session Configuration
SESSION_COOKIE_SECURE = SSL_ENABLED
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

def validate_soil_params(nitrogen, phosphorus, potassium, ph):
    """Validate soil parameters against defined limits."""
    try:
        if not (SOIL_PARAMS_LIMITS['nitrogen']['min'] <= float(nitrogen) <= SOIL_PARAMS_LIMITS['nitrogen']['max']):
            return False
        if not (SOIL_PARAMS_LIMITS['phosphorus']['min'] <= float(phosphorus) <= SOIL_PARAMS_LIMITS['phosphorus']['max']):
            return False
        if not (SOIL_PARAMS_LIMITS['potassium']['min'] <= float(potassium) <= SOIL_PARAMS_LIMITS['potassium']['max']):
            return False
        if not (SOIL_PARAMS_LIMITS['ph']['min'] <= float(ph) <= SOIL_PARAMS_LIMITS['ph']['max']):
            return False
        return True
    except (ValueError, TypeError):
        return False 