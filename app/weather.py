import requests
from flask import request, Blueprint
import logging
import os

CURRNET_WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
FORECAST_WEATHER_API_URL = "http://api.weatherapi.com/v1/forecast.json"
MAX_FORECAST_DAY = 14
WEATHER_API_KEY = os.environ['WEATHER_API_KEY']

logger = logging.getLogger(__name__)

weather_blueprint = Blueprint('weather', __name__)

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


@weather_blueprint.route("/forecast")
def get_forecast_weather():
    location = request.args.get('location')
    days_ahead = request.args.get('days')

    if location is None:
        return {"error": "location cannot be None"}, 400

    if days_ahead is None or int(days_ahead) > MAX_FORECAST_DAY:
        return {"error": f"No days ahead provided or requested forecast more than {MAX_FORECAST_DAY} ahead"}, 400
    
    logger.info(f"Getting forecast weather for {location} with {days_ahead}")

    params = {
        "key": WEATHER_API_KEY,
        "q": location,
        "days": days_ahead,
    }

    response = requests.get(FORECAST_WEATHER_API_URL, params=params)
    if response.status_code == 200:
        return response.json(), 200

    logger.error(f"Error when calling get forecast weather API for {location}, code: {response.status_code}")
    logger.error(response.json())
    
    return {"error": "Error fetching the data"}, response.status_code
    