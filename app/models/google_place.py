from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel

class Review(BaseModel):
    text: str

    class Config:
        extra = "ignore"

class GetPlaceReviewsResponse(BaseModel):
    rating: Optional[float] = None
    reviews: Optional[List[Review]] = None
    user_rating_total: Optional[int] = None

    class Config:
        extra = "ignore"


class GetDirectionResponse(BaseModel):
    distance: str
    duration: str


class CombinedPlaceDetailResponse(BaseModel):
    place_id: str = '123'
    place_name: str
    place_google_map_url: Optional[str] = None
    review: Optional[GetPlaceReviewsResponse] = None
    direction_to_previous_distination: Optional[GetDirectionResponse] = None
