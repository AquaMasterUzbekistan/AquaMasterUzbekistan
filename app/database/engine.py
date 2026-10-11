import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import settings

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL
engine_kwargs = {"echo": False}
if "sqlite" not in db_url:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True

from sqlalchemy import event

try:
    engine = create_async_engine(db_url, **engine_kwargs)
except ModuleNotFoundError as e:
    logger.warning(
        "Database driver not found for %s (%s). Falling back to sqlite+aiosqlite:///app.db",
        db_url,
        e,
    )
    engine = create_async_engine("sqlite+aiosqlite:///app.db", echo=False)

if "sqlite" in str(engine.url):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.close()
        except Exception:
            pass

