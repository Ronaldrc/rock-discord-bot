# 1h, 3h, 6h, 12h, 24h
# 24*7, 24*14, 14*30

# 2d, 7d, 14d, 30d

from db.db_init import (
    Death,
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
###### Player kill table
##########################
async def get_sum_deaths_db(
    async_session: async_sessionmaker,
    data: dict
):
    """
    Return the sum of deaths estimated value for one rsn
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of drop values for {data.get('rsn')} from db")
            stmt = (
                select(Death.rsn, sum(Death.loot_big_int))
                .where(Death.rsn == data.get('rsn'))
            )
            result = await session.execute(stmt)
            drop = result.scalar()
            if drop:
                return drop.loot_big_int
            else:
                return "N/A"
        except Exception as e:
            logger.error(f"Failed to get drop for {data.get('rsn')} to db: {e}")
            await session.rollback()


# Use for Recent Total GP
async def get_all_deaths_sum_values_db(
    async_session: async_sessionmaker,
    time_range_hours: int = None
):
    """

    Parameter
    ----------
    async_session: async_sessionmaker
        
    
    time_range_hours: int
        In hours, retrieve data from now to time_range_hours hours ago.
        If None, sum all deaths for all rsn

    Return the sum of deaths estimated value for all rsn, in descending order
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of deaths estimated value for all rsn from db")
            stmt = (
                select(Death.rsn, sum(Death.loot_big_int))
                .group_by(Death.rsn)
                .order_by(sum(Death.loot_big_int).desc())
            )
            if time_range_hours is not None:
                stmt.where(Death.date >= datetime.now() - timedelta(hours=time_range_hours))
            result = await session.execute(stmt)
            rows = result.all()
            return rows if rows else None   # Return all rows, row is a tuple
        except Exception as e:
            logger.error(f"Failed to get sum of deaths estimated value for all rsn from db: {e}")
            await session.rollback()


async def insert_death_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            logger.info(f"Inserting death for {data.get('rsn')} to db")
            new_drop = Death(
                rsn=data.get('rsn'),
                loot_big_int=data.get('loot_big_int'),
                loot_string=data.get('loot_string')
            )
            session.add(new_drop)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to add death for {data.get('rsn')} to db: {e}")
            await session.rollback()
