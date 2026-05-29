from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    source_id: int
    external_id: str | None = None
    name: str
    url: str
    parent_id: int | None = None
    is_enabled: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    parent_id: int | None = None
    is_enabled: bool | None = None


class CategorySyncRequest(BaseModel):
    source_id: int


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

