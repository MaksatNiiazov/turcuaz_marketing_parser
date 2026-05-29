from app.db.session import SessionLocal
from app.modules.market_parser.repositories.source_repo import SourceRepository
from app.modules.market_parser.schemas.source import SourceCreate


def bootstrap_market_parser() -> None:
    with SessionLocal() as db:
        repo = SourceRepository(db)
        if repo.get_by_code("globus") is None:
            repo.create(
                SourceCreate(
                    name="Globus Online",
                    code="globus",
                    base_url="https://globus-online.kg/ru-kg",
                    type="html",
                    is_active=True,
                )
            )
            db.commit()

