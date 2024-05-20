from functools import wraps
from db.engine import async_session
from sqlalchemy.exc import SQLAlchemyError, OperationalError


def db_session(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with async_session() as session:
            async with session.begin():
                try:
                    return await func(self, session, *args, **kwargs)
                except (SQLAlchemyError, OperationalError) as e:
                    await session.rollback()
                    raise e
    return wrapper
