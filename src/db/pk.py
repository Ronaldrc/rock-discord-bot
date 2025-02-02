# 1h, 3h, 6h, 12h, 24h
# 24*7, 24*14, 14*30

# 2d, 7d, 14d, 30d

from db.db_init import (
    PlayerKill,
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
async def get_sum_pk_db(
    async_session: async_sessionmaker,
    data: dict
):
    """
    Return the sum of player kill estimated value for one rsn
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of drop values for {data.get('rsn')} from db")
            stmt = (
                select(PlayerKill.rsn, sum(PlayerKill.loot_big_int))
                .where(PlayerKill.rsn == data.get('rsn'))
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
async def get_all_pk_sum_values_db(
    async_session: async_sessionmaker,
    time_range_hours: int = None
):
    """

    Parameter
    ----------
    async_session: async_sessionmaker
        
    
    time_range_hours: int
        In hours, retrieve data from now to time_range_hours hours ago.
        If None, sum all drops for all rsn

    Return the sum of player kill estimated value for all rsn, in descending order
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting sum of player kill estimated value for all rsn from db")
            stmt = (
                select(PlayerKill.rsn, sum(PlayerKill.loot_big_int))
                .group_by(PlayerKill.rsn)
                .order_by(sum(PlayerKill.loot_big_int).desc())
            )
            if time_range_hours is not None:
                stmt.where(PlayerKill.date >= datetime.now() - timedelta(hours=time_range_hours))
            result = await session.execute(stmt)
            rows = result.all()
            return rows if rows else None   # Return all rows, row is a tuple
        except Exception as e:
            logger.error(f"Failed to get sum of player kill estimated value for all rsn from db: {e}")
            await session.rollback()


async def insert_player_kill_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            logger.info(f"Inserting player kill for {data.get('rsn')} to db")
            new_drop = PlayerKill(
                rsn=data.get('rsn'),
                loot_big_int=data.get('loot_big_int'),
                loot_string=data.get('loot_string')
            )
            session.add(new_drop)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to add player kill for {data.get('rsn')} to db: {e}")
            await session.rollback()
