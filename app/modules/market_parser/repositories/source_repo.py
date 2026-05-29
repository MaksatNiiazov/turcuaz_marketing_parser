from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.market_parser.models.entities import ParserSource
from app.modules.market_parser.schemas.source import SourceCreate, SourceUpdate


class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[ParserSource]:
        result = self.db.execute(select(ParserSource).order_by(ParserSource.id))
        return list(result.scalars().all())

    def get(self, source_id: int) -> ParserSource | None:
        return self.db.get(ParserSource, source_id)

    def get_by_code(self, code: str) -> ParserSource | None:
        result = self.db.execute(select(ParserSource).where(ParserSource.code == code))
        return result.scalar_one_or_none()

    def create(self, payload: SourceCreate) -> ParserSource:
        source = ParserSource(**payload.model_dump())
        self.db.add(source)
        self.db.flush()
        return source

    def patch(self, source: ParserSource, payload: SourceUpdate) -> ParserSource:
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(source, key, value)
        self.db.flush()
        return source
