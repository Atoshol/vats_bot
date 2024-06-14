import asyncio
from db.engine import engine, Base
from db.models.client import Client
from db.models.admin import Admin
from db.models.user import User
from db.models.token import TokenLink, TokenPair
from db.models.user_settings import UserSettings
from db.models.message import Message, MessageLastIndex
from db.models.default import Settings


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
