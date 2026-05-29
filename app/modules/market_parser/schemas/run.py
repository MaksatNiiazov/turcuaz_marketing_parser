from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunCreate(BaseModel):
    source_id: int
    category_ids: list[int] = Field(default_factory=list)
    parse_all_enabled: bool = False
    created_by: str | None = None


class RunCategoryRead(BaseModel):
    id: int
    run_id: int
    category_id: int
    status: str
    products_found: int
    products_saved: int
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RunRead(BaseModel):
    id: int
    source_id: int
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    total_categories: int
    processed_categories: int
    total_products: int
    saved_products: int
    error_message: str | None
    created_by: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

