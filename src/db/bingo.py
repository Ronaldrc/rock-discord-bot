from db.db_init import (
    BingoDrop,
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

async def get_bingo_drop_rsn_db(
    async_session: async_sessionmaker,
    data: dict
):
    """
    Get the bingo drop using RSN
    """
    logger.info("finish get_bingo_drop_rsn_db function")


async def get_all_bingo_drop_db(
    async_session: async_sessionmaker,
    time_range_hours: int = None
):
    """
    Get all bingo drops using a time range

    If not time_range is used, all bingo drops from then table will be retrieved.
    """
    logger.info("finish get_all_bingo_drop_db function")


async def insert_bingo_drop_db(
    async_session: async_sessionmaker,
    data: dict
):
    """
    Insert a bingo drop
    """
    async with async_session() as session:
        try:
            logger.info(f"Inserting bingo drop for {data.get('rsn')} to db")
            new_drop = BingoDrop(
                rsn=data.get('rsn'),
                item=data.get('item'),
                team_name=data.get('team_name')
            )
            session.add(new_drop)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to add bingo drop for {data.get('rsn')} to db: {e}")
            await session.rollback()