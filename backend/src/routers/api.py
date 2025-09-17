from fastapi import APIRouter, Depends
from src.security import verify_api_key
from src.schemas import *
from src.models import *
from sqlalchemy import func

router = APIRouter(dependencies=[Depends(verify_api_key)])

DEFAULT_LIMIT = 10
MAX_LIMIT = 100


EARTH_RADIUS = 6371


def get_haversine_distance_expression(central_lat: float, central_lon: float):
    inner = func.sin(func.radians(central_lat)) * func.sin(
        func.radians(Building.latitude)
    ) + func.cos(func.radians(central_lat)) * func.cos(
        func.radians(Building.latitude)
    ) * func.cos(
        func.radians(Building.longitude) - func.radians(central_lon)
    )
    in_borders = func.least(func.greatest(inner, -1.0), 1.0)
    return EARTH_RADIUS * func.acos(in_borders)
