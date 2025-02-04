import requests
import json
from datetime import datetime
from config import WEATHER_API_KEY, WEATHER_API_BASE_URL, WEATHER_API_GEOCODING_URL, WEATHER_UNITS
import logging

def get_weather_data(latitude, longitude):
    try:
        # Get weather data
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': WEATHER_API_KEY,
            'units': WEATHER_UNITS
        }
        weather_response = requests.get(f"{WEATHER_API_BASE_URL}/weather", params=params)
        weather_data = weather_response.json()

        # Get location details using reverse geocoding
        geocoding_params = {
            'lat': latitude,
            'lon': longitude,
            'limit': 1,
            'appid': WEATHER_API_KEY
        }
        location_response = requests.get(f"{WEATHER_API_GEOCODING_URL}/reverse", params=geocoding_params)
        location_data = location_response.json()

        if location_data and len(location_data) > 0:
            location = location_data[0]
            region = f"{location.get('name', '')}, {location.get('state', '')}, {location.get('country', '')}"
        else:
            region = "Unknown Location"

        if weather_response.status_code == 200:
            return {
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'rainfall': weather_data.get('rain', {}).get('1h', 0),
                'region': region,
                'location_details': {
                    'district': location.get('name', 'Unknown'),
                    'state': location.get('state', 'Unknown'),
                    'country': location.get('country', 'Unknown')
                }
            }
        return None
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return None

def get_weather_data_old(city=None, latitude=None, longitude=None):
    """
    Get weather data using OpenWeatherMap API
    Can be called either with city name or latitude/longitude coordinates
    """
    try:
        # Validate inputs
        if latitude is not None:
            try:
                latitude = float(latitude)
            except (ValueError, TypeError):
                print("Error: Invalid latitude value")
                return None
                
        if longitude is not None:
            try:
                longitude = float(longitude)
            except (ValueError, TypeError):
                print("Error: Invalid longitude value")
                return None

        # Build the API URL with parameters
        params = {
            'appid': WEATHER_API_KEY,
            'units': WEATHER_UNITS
        }
        
        # Add either city or coordinates to parameters
        if city and city.strip():
            params['q'] = city.strip()
        elif latitude is not None and longitude is not None:
            params['lat'] = latitude
            params['lon'] = longitude
        else:
            print("Error: Either city name or both latitude and longitude must be provided")
            return None
        
        # Make the API request using the base URL
        weather_api_url = f"{WEATHER_API_BASE_URL}/weather"
        response = requests.get(weather_api_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        weather_data = response.json()
        
        # Validate the response data
        if 'main' not in weather_data or 'weather' not in weather_data:
            print("Error: Invalid response from weather API")
            return None
            
        # Extract relevant information
        result = {
            'temperature': float(weather_data['main']['temp']),
            'humidity': float(weather_data['main']['humidity']),
            'description': weather_data['weather'][0]['description'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rainfall': 0.0,  # Default value
            'region': weather_data.get('name', 'Unknown') + ', ' + weather_data.get('sys', {}).get('country', '')  # City name and country code
        }

        # Try to get rainfall data from rain field if it exists
        if 'rain' in weather_data:
            # OpenWeatherMap returns rain in mm for last 1h or 3h
            result['rainfall'] = float(weather_data['rain'].get('1h', 0.0))
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing weather data: {e}")
        return None
    except ValueError as e:
        print(f"Error converting weather data values: {e}")
        return None 