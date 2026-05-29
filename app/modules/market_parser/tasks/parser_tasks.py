from app.db.session import SessionLocal
from app.modules.market_parser.schemas.run import RunCreate
from app.modules.market_parser.services.parser_service import ParserService


async def run_market_parser(payload: RunCreate):
    with SessionLocal() as db:
        return await ParserService(db).run_parser(payload)


async def execute_market_parser_run(payload: RunCreate, run_id: int):
    with SessionLocal() as db:
        return await ParserService(db).execute_parser_run(payload, run_id)
