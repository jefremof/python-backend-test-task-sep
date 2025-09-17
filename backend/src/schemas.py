from __future__ import annotations
from pydantic import ConfigDict, BaseModel, Field
from typing import List

class PhoneReadSchema(BaseModel):
    id: int
    number: str

    model_config = ConfigDict(from_attributes=True)

class ActivityBaseReadSchema(BaseModel):
    id: int
    name: str
    parent_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class ActivityTreeReadSchema(ActivityBaseReadSchema):
    children: List[ActivityTreeReadSchema] = Field(default_factory=list)

class BuildingReadSchema(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float
    
    model_config = ConfigDict(from_attributes=True)

class OrganizationReadSchema(BaseModel):
    id: int
    name: str
    building: BuildingReadSchema
    phones: List[PhoneReadSchema] = Field(default_factory=list)
    activities: List[ActivityBaseReadSchema] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
