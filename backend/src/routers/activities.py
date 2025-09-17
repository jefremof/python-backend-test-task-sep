from fastapi import Depends, Query, Path, HTTPException
from src.schemas import *
from src.database import get_db
from src.models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc
from sqlalchemy.orm import selectinload

from src.routers.api import router, DEFAULT_LIMIT, MAX_LIMIT


@router.get("/activities", response_model=list[ActivityBaseReadSchema])
async def read_activities(
    session: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
):
    result = await session.execute(
        select(Activity).order_by(asc(Activity.id)).offset(offset).limit(limit)
    )
    return result.unique().scalars().all()


@router.get("/activities/{activity_id}", response_model=ActivityTreeReadSchema)
async def read_activity(
    session: AsyncSession = Depends(get_db),
    activity_id: int = Path(
        ..., gt=0, description="The ID of the activity to retrieve"
    ),
):
    result = await session.execute(
        select(Activity)
        .where(Activity.id == activity_id)
        .options(
            selectinload(Activity.parent),
            selectinload(Activity.children)
            .selectinload(Activity.children)
            .selectinload(Activity.children),
        )
    )
    activity = result.scalars().first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity
