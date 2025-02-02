from db.db_init import (
    PersonalBest
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
###### Personal-best table
##########################

# FIXME: the code is not right. fix get_all personal best so only 1pb per rsn 
async def get_all_personal_best_db(
    async_session: async_sessionmaker,
    time_range_hours: int = None
):
    """
    Return up to top 100 personal-best records, in descending order
    """
    async with async_session() as session:
        try:
            logger.info(f"Getting all personal bests for all rsn from db")
            stmt = (
                select(PersonalBest.rsn, PersonalBest.duration, PersonalBest.date)
                .group_by(PersonalBest.rsn)
                .order_by(PersonalBest.duration.asc())
            )
            if time_range_hours is not None:
                stmt.where(PersonalBest.date >= datetime.now() - timedelta(hours=time_range_hours))
            result = await session.execute(stmt)
            rows = result.all()
            return rows if rows else None
        except Exception as e:
            logger.error(f"Failed to get sum of drop values for all rsn from db: {e}")
            await session.rollback()


async def insert_personal_best_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            logger.info(f"Inserting personal best for {data.get('rsn')} to db")
            new_drop = PersonalBest(
                rsn=data.get('rsn'),
                duration=data.get('duration')
            )
            session.add(new_drop)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to add personal best for {data.get('rsn')} to db: {e}")
            await session.rollback()
