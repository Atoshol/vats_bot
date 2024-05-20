from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from decorators.db_session import db_session


class AsyncCRUD:
    def __init__(self, model):
        self.model = model

    @db_session
    async def create(self, session, **kwargs):
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        return instance

    @db_session
    async def read(self, session, id_):
        query = select(self.model).where(self.model.id == id_)
        result = await session.execute(query)
        try:
            return result.scalars().one()
        except NoResultFound:
            return None

    @db_session
    async def update(self, session, id_, **kwargs):
        query = select(self.model).where(self.model.id == id_)
        result = await session.execute(query)
        try:
            instance = result.scalars().one()
            for attr, value in kwargs.items():
                setattr(instance, attr, value)
            await session.commit()
            return instance
        except NoResultFound:
            return None

    @db_session
    async def delete(self, session, id_):
        query = select(self.model).where(self.model.id == id_)
        result = await session.execute(query)
        try:
            instance = result.scalars().one()
            await session.delete(instance)
            await session.commit()
        except NoResultFound:
            return None
