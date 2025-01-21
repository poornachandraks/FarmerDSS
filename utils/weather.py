import datetime
import requests
import logging
from config import (
    METEOMATICS_USERNAME, 
    METEOMATICS_PASSWORD, 
    METEOMATICS_BASE_URL,
    WEATHER_PARAMS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_weather_data(latitude, longitude):
    """
    Fetch weather data from Meteomatics API
    """
    try:
        now = datetime.datetime.utcnow()
        
        # Parameters for current weather
        current_params = ",".join([
            "t_2m:C",                    # Temperature at 2m in Celsius
            "relative_humidity_2m:p",     # Relative humidity at 2m in %
            "precip_24h:mm"              # 24h precipitation in mm
        ])
        
        # Get current weather data
        current_url = f"{METEOMATICS_BASE_URL}/{now.strftime('%Y-%m-%dT%H:%M:%SZ')}/{current_params}/{latitude},{longitude}/json"
        logger.info(f"Fetching current weather from: {current_url}")
        
        response = requests.get(
            current_url,
            auth=(METEOMATICS_USERNAME, METEOMATICS_PASSWORD)
        )
        
        if response.status_code == 200:
            data = response.json()
            
            try:
                weather_data = {
                    'temperature': data['data'][0]['coordinates'][0]['dates'][0]['value'],
                    'humidity': data['data'][1]['coordinates'][0]['dates'][0]['value'],
                    'rainfall': data['data'][2]['coordinates'][0]['dates'][0]['value'],
                    'region': 'Local Area'
                }
                
                logger.info(f"Processed weather data: {weather_data}")
                return weather_data
                
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing current weather data: {e}")
                return None
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return None 