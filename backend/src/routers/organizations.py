from fastapi import Depends, Query, Path, HTTPException
from src.schemas import *
from src.database import get_db
from src.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, asc, func
from sqlalchemy.orm import selectinload, joinedload, aliased

from src.routers.api import (
    router,
    DEFAULT_LIMIT,
    MAX_LIMIT,
    get_haversine_distance_expression,
)

_ORG_OPTIONS = (
    joinedload(Organization.building),
    selectinload(Organization.phones),
    selectinload(Organization.activities),
)


@router.get("/organizations", response_model=list[OrganizationReadSchema])
async def read_organizations(
    session: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/organizations/{organization_id}", response_model=OrganizationReadSchema)
async def read_organization(
    session: AsyncSession = Depends(get_db),
    organization_id: int = Path(
        ..., gt=0, description="The ID of the organization to retrieve"
    ),
):
    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .where(Organization.id == organization_id)
    )
    organization = result.scalars().first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get(
    "/organizations/by_building/{building_id}",
    response_model=list[OrganizationReadSchema],
)
async def read_organizations_by_building(
    session: AsyncSession = Depends(get_db),
    building_id: int = Path(
        ..., gt=0, description="The ID of the building to retrieve organization from"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .where(Organization.building_id == building_id)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    organizations = result.unique().scalars().all()
    return organizations


@router.get(
    "/organizations/by_activity/{activity_id}",
    response_model=list[OrganizationReadSchema],
)
async def read_organization_by_activity(
    session: AsyncSession = Depends(get_db),
    activity_id: int = Path(
        ..., gt=0, description="The ID of the activity to retrieve organizations with"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):

    activity_check = await session.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    if not activity_check.scalars().first():
        raise HTTPException(status_code=404, detail=f"Activity not found.")

    exists_subquery = select(1).where(
        org_act_assoc.c.organization_id == Organization.id,
        org_act_assoc.c.activity_id == activity_id,
    )

    result = await session.execute(
        select(Organization)
        .where(exists(exists_subquery))
        .options(*_ORG_OPTIONS)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    organizations = result.scalars().all()
    return organizations


@router.get("/organizations/by_activity/", response_model=list[OrganizationReadSchema])
async def read_organization_by_activity_name(
    session: AsyncSession = Depends(get_db),
    name: str = Query(
        ...,
        min_length=1,
        description="Name of the activity to search organizations with",
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    activity_obj = await session.execute(
        select(Activity).where(func.lower(Activity.name) == func.lower(name))
    )
    found_activity = activity_obj.scalars().first()
    if not found_activity:
        raise HTTPException(status_code=404, detail=f"Activity not found.")

    exists_subquery = select(1).where(
        org_act_assoc.c.organization_id == Organization.id,
        org_act_assoc.c.activity_id == found_activity.id,
    )

    result = await session.execute(
        select(Organization)
        .where(exists(exists_subquery))
        .options(*_ORG_OPTIONS)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    organizations = result.scalars().all()
    return organizations


@router.get(
    "/organizations/by_activity_branch/{activity_id}",
    response_model=list[OrganizationReadSchema],
)
async def read_organization_by_activity_branch(
    session: AsyncSession = Depends(get_db),
    activity_id: int = Path(
        ..., gt=0, description="The ID of the activity to retrieve organizations with"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):

    activity_check = await session.execute(
        select(Activity).where(Activity.id == activity_id)
    )
    if not activity_check.scalars().first():
        raise HTTPException(status_code=404, detail=f"Activity not found.")

    recursive_cte = (
        select(Activity.id)
        .where(Activity.id == activity_id)
        .cte(name="activity_branch", recursive=True)
    )

    aliased_activities = aliased(Activity)
    recursive_cte = recursive_cte.union_all(
        select(aliased_activities.id).where(
            aliased_activities.parent_id == recursive_cte.c.id
        )
    )

    exists_subquery = select(1).where(
        org_act_assoc.c.organization_id == Organization.id,
        org_act_assoc.c.activity_id.in_(select(recursive_cte.c.id)),
    )

    result = await session.execute(
        select(Organization)
        .where(exists(exists_subquery))
        .options(*_ORG_OPTIONS)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    organizations = result.scalars().all()
    return organizations


@router.get(
    "/organizations/by_activity_branch/", response_model=list[OrganizationReadSchema]
)
async def read_organization_by_activity_branch_name(
    session: AsyncSession = Depends(get_db),
    name: str = Query(
        ...,
        min_length=1,
        description="Name of the activity to search organizations with",
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    activity_obj = await session.execute(
        select(Activity).where(func.lower(Activity.name) == func.lower(name))
    )
    found_activity = activity_obj.scalars().first()
    if not found_activity:
        raise HTTPException(status_code=404, detail=f"Activity not found.")

    recursive_cte = (
        select(Activity.id)
        .where(Activity.id == found_activity.id)
        .cte(name="activity_branch", recursive=True)
    )

    aliased_activities = aliased(Activity)
    recursive_cte = recursive_cte.union_all(
        select(aliased_activities.id).where(
            aliased_activities.parent_id == recursive_cte.c.id
        )
    )

    exists_subquery = select(1).where(
        org_act_assoc.c.organization_id == Organization.id,
        org_act_assoc.c.activity_id.in_(select(recursive_cte.c.id)),
    )

    result = await session.execute(
        select(Organization)
        .where(exists(exists_subquery))
        .options(*_ORG_OPTIONS)
        .order_by(asc(Organization.id))
        .offset(offset)
        .limit(limit)
    )
    organizations = result.scalars().all()
    return organizations


@router.get("/organizations/by_name/", response_model=OrganizationReadSchema)
async def read_organization_by_name(
    session: AsyncSession = Depends(get_db),
    name: str = Query(
        ...,
        min_length=1,
        description="Name of the organization to search for",
    ),
):
    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .where(func.lower(Organization.name) == func.lower(name))
    )
    organization = result.scalars().first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/organizations/in_radius/", response_model=List[OrganizationReadSchema])
async def read_organizations_in_radius(
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

    buildings_in_radius_select = (
        select(Building.id)
        .where(haversine_distance_expression <= radius_km)
        .subquery("buildings_in_radius")
    )

    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .join(
            buildings_in_radius_select,
            Organization.building_id == buildings_in_radius_select.c.id,
        )
        .offset(offset)
        .limit(limit)
    )
    organizations = result.unique().scalars().all()
    return organizations


@router.get("/organizations/in_rectangle/", response_model=List[OrganizationReadSchema])
async def read_organizations_in_rectangle(
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

    buildings_in_rectangle_select = (
        select(Building.id)
        .where(
            Building.latitude.between(min_latitude, max_latitude),
            Building.longitude.between(min_longitude, max_longitude),
        )
        .subquery("buildings_in_rectangle")
    )

    result = await session.execute(
        select(Organization)
        .options(*_ORG_OPTIONS)
        .join(
            buildings_in_rectangle_select,
            Organization.building_id == buildings_in_rectangle_select.c.id,
        )
        .offset(offset)
        .limit(limit)
    )
    organizations = result.unique().scalars().all()
    return organizations
