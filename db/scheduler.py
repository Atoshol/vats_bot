import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.sql import text

from db.engine import async_session


async def delete_expired_messages():
    async with async_session() as session:
        # SQL command to delete messages where the expire_time is less than the current Unix timestamp
        delete_query = text("DELETE FROM message WHERE expire_time <= EXTRACT(EPOCH FROM NOW())")
        await session.execute(delete_query)
        await session.commit()
        print("Expired messages deleted successfully.")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Schedule 'delete_expired_messages' to run every minute
    scheduler.add_job(delete_expired_messages, 'interval', minutes=1)
    scheduler.start()
    print("Scheduler started. Deleting expired messages every minute.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(delete_expired_messages())  # Run once at startup
    start_scheduler()
    asyncio.get_event_loop().run_forever()
