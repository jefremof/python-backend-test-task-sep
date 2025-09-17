from fastapi import Depends, Query, Path, HTTPException
from src.schemas import *
from src.database import get_db
from src.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc

from src.routers.api import (
    router,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    get_haversine_distance_expression,
)


@router.get("/buildings", response_model=list[BuildingReadSchema])
async def read_buildings(
    session: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    result = await session.execute(
        select(Building).order_by(asc(Building.id)).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/buildings/{building_id}", response_model=BuildingReadSchema)
async def read_building(
    session: AsyncSession = Depends(get_db),
    building_id: int = Path(
        ..., gt=0, description="The ID of the building to retrieve"
    ),
):
    result = await session.execute(select(Building).where(Building.id == building_id))
    building = result.scalars().first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.get("/buildings/in_radius/", response_model=List[BuildingReadSchema])
async def read_buildings_in_radius(
    session: AsyncSession = Depends(get_db),
    latitude: float = Query(..., description="Latitude of the center point"),
    longitude: float = Query(..., description="Longitude of the center point"),
    radius_km: float = Query(..., gt=0, description="Radius in kilometers"),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    haversine_distance_expression = get_haversine_distance_expression(
        latitude, longitude
    )

    result = await session.execute(
        select(Building)
        .where(haversine_distance_expression <= radius_km)
        .offset(offset)
        .limit(limit)
    )
    buildings = result.scalars().all()
    return buildings


@router.get("/buildings/in_rectangle/", response_model=List[BuildingReadSchema])
async def read_buildings_in_rectangle(
    session: AsyncSession = Depends(get_db),
    latitude: float = Query(..., description="Latitude of the center point"),
    longitude: float = Query(..., description="Longitude of the center point"),
    width: float = Query(..., gt=0, description="Rectangle width in degrees"),
    height: float = Query(..., gt=0, description="Rectangle height in degrees"),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    min_latitude = latitude - (height / 2)
    max_latitude = latitude + (height / 2)
    min_longitude = longitude - (width / 2)
    max_longitude = longitude + (width / 2)

    result = await session.execute(
        select(Building)
        .where(
            Building.latitude.between(min_latitude, max_latitude),
            Building.longitude.between(min_longitude, max_longitude),
        )
        .offset(offset)
        .limit(limit)
    )
    buildings = result.scalars().all()
    return buildings
