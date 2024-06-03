import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.sql import text

from db.engine import async_session


async def deactivate_expired_users():
    async with async_session() as session:
        # SQL command to deactivate users where the sub_expire_time is less than the current Unix timestamp
        deactivate_query = text("UPDATE \"user\" SET payed = 0 WHERE sub_expire_time <= EXTRACT(EPOCH FROM NOW())")
        await session.execute(deactivate_query)
        await session.commit()
        print("Expired users deactivated successfully.")


def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Schedule 'deactivate_expired_users' to run every minute
    scheduler.add_job(deactivate_expired_users, 'interval', minutes=1)
    scheduler.start()
    print("Scheduler started. Deactivating expired users every minute.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(deactivate_expired_users())  # Run once at startup
    start_scheduler()
    asyncio.get_event_loop().run_forever()
