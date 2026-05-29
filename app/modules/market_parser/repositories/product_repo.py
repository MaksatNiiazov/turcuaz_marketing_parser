from __future__ import annotations

from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.modules.market_parser.models.entities import MarketProduct, ParserCategory


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        source_id: int | None = None,
        category_id: int | None = None,
        name: str | None = None,
        sku: str | None = None,
    ) -> list[MarketProduct]:
        stmt = select(MarketProduct).order_by(MarketProduct.name)
        if source_id is not None:
            stmt = stmt.where(MarketProduct.source_id == source_id)
        if category_id is not None:
            stmt = stmt.where(MarketProduct.category_id.in_(self._category_scope_ids(category_id)))
        if name:
            stmt = stmt.where(MarketProduct.name.ilike(f"%{name}%"))
        if sku:
            stmt = stmt.where(MarketProduct.external_sku.ilike(f"%{sku}%"))
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def _category_scope_ids(self, category_id: int) -> list[int]:
        child_ids = list(
            self.db.execute(
                select(ParserCategory.id).where(ParserCategory.parent_id == category_id)
            ).scalars().all()
        )
        return [category_id, *child_ids]

    def get(self, product_id: int) -> MarketProduct | None:
        return self.db.get(MarketProduct, product_id)

    def get_by_sku(self, source_id: int, external_sku: str) -> MarketProduct | None:
        result = self.db.execute(
            select(MarketProduct).where(
                and_(MarketProduct.source_id == source_id, MarketProduct.external_sku == external_sku)
            )
        )
        return result.scalar_one_or_none()

    def upsert(
        self,
        source_id: int,
        category_id: int | None,
        external_sku: str,
        name: str,
        unit: str | None,
        image_url: str | None,
        product_url: str | None,
        seen_at: datetime,
    ) -> MarketProduct:
        product = self.get_by_sku(source_id, external_sku)
        if product is None:
            product = MarketProduct(
                source_id=source_id,
                category_id=category_id,
                external_sku=external_sku,
                name=name,
                unit=unit,
                image_url=image_url,
                product_url=product_url,
                first_seen_at=seen_at,
                last_seen_at=seen_at,
            )
            self.db.add(product)
        else:
            product.category_id = category_id
            product.name = name
            product.unit = unit
            product.image_url = image_url
            product.product_url = product_url
            product.last_seen_at = seen_at
            product.is_active = True
        self.db.flush()
        return product
