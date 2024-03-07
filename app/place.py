import requests
import os
from flask import request, Blueprint
import logging
from typing import Optional, List, Any

from app.models.google_place import GetPlaceReviewsResponse, GetDirectionResponse, CombinedPlaceDetailResponse

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# URLS
FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
PLACE_URL_FROM_ID = "https://www.google.com/maps/place"
PLACE_DETAIL_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GOOGLE_ROUTES_API = "https://maps.googleapis.com/maps/api/directions/json"

# Fields for Google Place Details API
URL = 'url'
REVIEWS = 'reviews'
RATING = 'rating'
USER_RATING_TOTAL = 'user_ratings_total'

logger = logging.getLogger(__name__)
place_bp = Blueprint('place', __name__)
logger.setLevel(logging.DEBUG)

def get_place_id_from_location(location: str) -> Optional[str]:
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
            return places[0].get('place_id')
    return None

def _get_place_details_by_place_id(place_id, fields: List[str]) -> dict:
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY,
        "fields": ','.join(fields),
    }

    repsonse = requests.get(PLACE_DETAIL_URL, params=params)
    if repsonse.status_code == 200:
        return repsonse.json().get('result')
    return {}

def get_place_reviews_from_place_id(place_id: str) -> Optional[GetPlaceReviewsResponse]:
    result = _get_place_details_by_place_id(
        place_id=place_id,
        fields=[REVIEWS, RATING, USER_RATING_TOTAL],
    )
    if result:
        return GetPlaceReviewsResponse(
            rating=result.get(RATING), 
            reviews=result.get(REVIEWS), 
            user_rating_total=result.get(USER_RATING_TOTAL)
        )
    return None

def get_directions(origin: str, destination: str) -> Optional[GetDirectionResponse]:
    # https://developers.google.com/maps/documentation/directions/get-directions
    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(GOOGLE_ROUTES_API, params=params)
    if response.status_code == 200:
        result = response.json()
        if len(result.get('routes')) == 0:
            return None
        distance = result.get('routes')[0].get('legs')[0].get('distance').get('text')
        duration = result.get('routes')[0].get('legs')[0].get('duration').get('text')
        return GetDirectionResponse(distance=distance, duration=duration)
    
    return None 


def _get_combined_info(location: str, last_location: Optional[str]) -> CombinedPlaceDetailResponse:
    place_id = get_place_id_from_location(location=location)
    response = CombinedPlaceDetailResponse(place_name=location)

    def get_review_from_details(details: dict):
        return GetPlaceReviewsResponse(
            rating=details.get(RATING), 
            reviews=details.get(REVIEWS), 
            user_rating_total=details.get(USER_RATING_TOTAL)
        )

    if place_id is None:
        return response
    
    place_detail_response: Optional[dict] = _get_place_details_by_place_id(
        place_id=place_id,
        fields=[URL, RATING, USER_RATING_TOTAL, REVIEWS]
    )

    response.place_name = location
    response.place_id = place_id
    response.place_google_map_url = place_detail_response.get(URL)
    response.review = get_review_from_details(place_detail_response)

    if last_location:
        direction_response: Optional[GetDirectionResponse] = get_directions(origin=location, destination=last_location)
        response.direction_to_previous_distination = direction_response
    return response 


@place_bp.route('find')
def find_place():
    location = request.args.get('location')
    if location is None:
        return {'error': 'location must be included in the requests'}, 400
    
    place_id: Optional[str] = get_place_id_from_location(location=location)

    if place_id is not None:
        # Returning the first place ID found
        url = generate_place_url_from_place_id(place_id)
        return {"place_url": url}, 200

    return {"error": "Place not found"}, 400


@place_bp.route("reviews")
def get_reviews():
    location = request.args.get('location')
    if not location:
        return {"error": "Location is not included in the request."}, 400
    
    place_id: Optional[str] = get_place_id_from_location(location=location)
    if not place_id:
        return {"error": "Place not found."}, 400
    
    reviews_response: Optional[GetPlaceReviewsResponse] = get_place_reviews_from_place_id(
        place_id=place_id,
    )

    if reviews_response is not None:
        return reviews_response.model_dump(), 200
    return {"error": "Place not found."}, 400
    

@place_bp.route("compute-routes", methods=['GET'])
def get_routes():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    if not origin or not destination:
        return {'error': "origin or destination is missing"}, 400
    
    result: Optional[GetDirectionResponse] = get_directions(origin=origin, destination=destination)
    if not result:
        return {'error': "origin or destination is missing"}, 400
    
    return result.model_dump(), 200

@place_bp.route('combined-planning')
def get_combined_info():
    locations = request.args.getlist('location')
    if not locations:
        return {'error': "location has to be present in the query parameter"}, 400
    
    responses: List[dict] = []
    for i, loc in enumerate(locations):
        if i:
            resp = _get_combined_info(location=loc, last_location=locations[i-1])
        else:
            resp = _get_combined_info(location=loc, last_location=None)
        if resp is not None:
            responses.append(resp.model_dump())
    
    return {'results': responses }, 200

def generate_place_url_from_place_id(place_id):
    result: Optional[dict] = _get_place_details_by_place_id(place_id, fields=['url'])
    if result is not None:
        return result.get('url')
    
    # some stackoverflow way of generating the url based on place id
    return f'{PLACE_URL_FROM_ID}/?q=place_id:{place_id}'
