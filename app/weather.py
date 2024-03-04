import requests
from flask import request, Blueprint
import logging
import os

CURRNET_WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']

logger = logging.getLogger(__name__)

weather_blueprint= Blueprint('weather', __name__)

@weather_blueprint.route('/current')
def get_current_weather():
    location = request.args.get('location')
    logger.info(f"Getting current weather data for {location}")
    params = {
        "key": WEATHER_API_KEY,
        "q": location,
    }
    
    response = requests.get(CURRNET_WEATHER_API_URL, params=params)
    if response.status_code == 200:
        return response.json(), 200

    logger.error(f"Error when calling get current weather API for {location}, code: {response.status_code}")
    logger.error(response.json())
    
    return {"error": "Error fetching the data"}, response.status_code