import asyncio
from bot.handlers import exe_bot
from db.create_tables import create_tables


if __name__ == "__main__":
    asyncio.run(create_tables())
    asyncio.run(exe_bot())
