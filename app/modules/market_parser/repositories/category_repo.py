from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.market_parser.models.entities import ParserCategory
from app.modules.market_parser.schemas.category import CategoryCreate, CategoryUpdate

TECHNICAL_CATEGORY_ID = re.compile(r"^[a-f0-9]{32}$")


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, source_id: int | None = None, enabled_only: bool = False) -> list[ParserCategory]:
        stmt = select(ParserCategory).order_by(ParserCategory.is_enabled.desc(), ParserCategory.name)
        if source_id is not None:
            stmt = stmt.where(ParserCategory.source_id == source_id)
        if enabled_only:
            stmt = stmt.where(ParserCategory.is_enabled.is_(True))
        result = self.db.execute(stmt)
        return [category for category in result.scalars().all() if not self._is_technical_category(category)]

    def list_by_ids(self, ids: list[int]) -> list[ParserCategory]:
        if not ids:
            return []
        result = self.db.execute(select(ParserCategory).where(ParserCategory.id.in_(ids)))
        return list(result.scalars().all())

    def list_child_categories(self, parent_ids: list[int], enabled_only: bool = False) -> list[ParserCategory]:
        if not parent_ids:
            return []
        stmt = select(ParserCategory).where(ParserCategory.parent_id.in_(parent_ids))
        if enabled_only:
            stmt = stmt.where(ParserCategory.is_enabled.is_(True))
        result = self.db.execute(stmt.order_by(ParserCategory.name))
        return list(result.scalars().all())

    def get(self, category_id: int) -> ParserCategory | None:
        return self.db.get(ParserCategory, category_id)

    def get_by_external_id(self, source_id: int, external_id: str) -> ParserCategory | None:
        result = self.db.execute(
            select(ParserCategory).where(
                ParserCategory.source_id == source_id,
                ParserCategory.external_id == external_id,
            )
        )
        return result.scalar_one_or_none()

    def create(self, payload: CategoryCreate) -> ParserCategory:
        category = ParserCategory(**payload.model_dump())
        self.db.add(category)
        self.db.flush()
        return category

    def upsert_many(self, items: list[CategoryCreate]) -> list[ParserCategory]:
        saved: list[ParserCategory] = []
        for item in items:
            category = None
            if item.external_id:
                category = self.get_by_external_id(item.source_id, item.external_id)
            if category is None:
                category = self.create(item)
            else:
                category.name = item.name
                category.url = item.url
                category.parent_id = item.parent_id
                if item.parent_id is None and item.is_enabled is False:
                    category.is_enabled = False
            saved.append(category)
        self.db.flush()
        return saved

    def has_children(self, category_id: int) -> bool:
        result = self.db.execute(
            select(ParserCategory.id).where(ParserCategory.parent_id == category_id).limit(1)
        )
        return result.scalar_one_or_none() is not None

    def disable_missing(self, source_id: int, external_ids: set[str]) -> int:
        stmt = select(ParserCategory).where(ParserCategory.source_id == source_id)
        if external_ids:
            stmt = stmt.where(ParserCategory.external_id.not_in(external_ids))
        categories = list(self.db.execute(stmt).scalars().all())
        for category in categories:
            category.is_enabled = False
        self.db.flush()
        return len(categories)

    def disable_parents_with_children(self, source_id: int) -> int:
        parent_ids = list(
            self.db.execute(
                select(ParserCategory.parent_id)
                .where(
                    ParserCategory.source_id == source_id,
                    ParserCategory.parent_id.is_not(None),
                )
                .distinct()
            ).scalars().all()
        )
        if not parent_ids:
            return 0
        parents = list(
            self.db.execute(
                select(ParserCategory).where(
                    ParserCategory.source_id == source_id,
                    ParserCategory.id.in_(parent_ids),
                )
            ).scalars().all()
        )
        for category in parents:
            category.is_enabled = False
        self.db.flush()
        return len(parents)

    def patch(self, category: ParserCategory, payload: CategoryUpdate) -> ParserCategory:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        self.db.flush()
        return category

    def set_enabled(self, category: ParserCategory, enabled: bool) -> ParserCategory:
        category.is_enabled = enabled
        self.db.flush()
        return category

    @staticmethod
    def _is_technical_category(category: ParserCategory) -> bool:
        return (
            category.external_id is not None
            and category.name == category.external_id
            and bool(TECHNICAL_CATEGORY_ID.match(category.external_id))
        )
