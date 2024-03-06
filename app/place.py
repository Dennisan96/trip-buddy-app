import requests
import os
from flask import request, Blueprint
import logging

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# URLS
FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
PLACE_URL_FROM_ID = "https://www.google.com/maps/place/?q=place_id:"

logger = logging.getLogger(__name__)
place_bp = Blueprint('place', __name__)

@place_bp.route('find')
def find_place():
    location = request.args.get('location')
    params = {
        'input': location,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': GOOGLE_API_KEY
    }

    response = requests.get(FIND_PLACE_URL, params=params)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the response JSON to get the place ID
        response_json = response.json()
        places = response_json.get('candidates')
        
        if places:
            # Returning the first place ID found
            place_id = places[0].get('place_id')
            url = generate_place_url_from_place_id(place_id)
            return {"place_url": url}, 200
        else:
            return {"error": "Place not found"}, 400
    else:
        return {"error": "Failed to connect to the Google Maps API"}, 500

def generate_place_url_from_place_id(place_id):
    return f'{PLACE_URL_FROM_ID}/?q=place_id:{place_id}'