from db.db_init import (
    Drop,
)
from sqlalchemy import (
    update,
    select
)
from sqlalchemy.sql.functions import sum
from sqlalchemy.ext.asyncio import async_sessionmaker
from config.logger_config import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)


##########################
###### Drop table
##########################
async def get_drop_sum_values_db(
    async_session: async_sessionmaker,
    data: dict
):
    """
    Return the sum of drop values for one rsn
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of drop values for {data.get('rsn')} from db")
            stmt = (
                select(Drop.rsn, sum(Drop.loot_big_int))
                .where(Drop.rsn == data.get('rsn'))
            )
            result = await session.execute(stmt)
            drop = result.scalar()  # drop is a tuple
            return drop[1] if drop else None    # return sum
        except Exception as e:
            logger.error(f"Failed to get sum of drop values for {data.get('rsn')} from db: {e}")
            await session.rollback()


# Use for Recent Total GP
async def get_all_drop_sum_values_db(
    async_session: async_sessionmaker,
    time_range_hours: int
):
    """

    Parameter
    ----------
    async_session: async_sessionmaker
        
    
    time_range_hours: int
        In hours, retrieve data from now to time_range_hours hours ago.

    Return the sum of drop values for all rsn, in descending order
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of drop values for all rsn from db")
            stmt = (
                select(Drop.rsn, sum(Drop.loot_big_int))
                .where(Drop.date >= datetime.now() - timedelta(hours=time_range_hours))
                .group_by(Drop.rsn)
                .order_by(sum(Drop.loot_big_int).desc())
            )
            result = await session.execute(stmt)
            rows = result.all()
            return rows if rows else None
        except Exception as e:
            logger.error(f"Failed to get sum of drop values for all rsn from db: {e}")
            await session.rollback()


async def insert_drop_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            logger.info(f"Inserting drop for {data.get('rsn')} to db")
            new_drop = Drop(
                rsn=data.get('rsn'),
                item=data.get('item'),
                loot_big_int=data.get('loot_big_int'),
                loot_string=data.get('loot_string')
            )
            session.add(new_drop)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to add drop for {data.get('rsn')} to db: {e}")
            await session.rollback()
