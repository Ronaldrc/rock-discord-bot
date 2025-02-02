from db.db_init import (
    Streamer,
)
from sqlalchemy import (
    update,
    select
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from config.logger_config import get_logger

logger = get_logger(__name__)


##########################
###### Streamer table
##########################
async def add_streamer_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            logger.info(f"Adding {data.get('name', "")} to db")
            new_streamer = Streamer(
                name=data.get('name'),
                title=data.get('title', "N/A"),
                is_live=data.get('is_live', False),
                stream_id=data.get('stream_id', -1),
                video_thumbnail=data.get("video_thumbnail", "N/A"),
                profile_pic=data.get('profile_pic', "N/A"),
                url=data.get('url', "N/A")
            )
            session.add(new_streamer)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed adding {data.get('name', "")} to db: {e}")
            await session.rollback()


async def update_streamer_db(async_session: async_sessionmaker, data: dict):
    async with async_session() as session:
        try:
            logger.info(f"Updating {data.get('name', "")} to db")
            stmt = (
                update(Streamer)
                .where(Streamer.name.ilike(data.get('name')))
                .values(**data)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed updating {data.get('name', "")} to db: {e}")
            await session.rollback()


# Add if new entry, else update
async def add_or_update_streamer_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            stmt = (
                select(Streamer)
                .where(Streamer.name.ilike(data.get('name')))
            )
            result = await session.execute(stmt)
            streamer = result.scalar()
            if streamer:
                await update_streamer_db(async_session, data)
            else:
                await add_streamer_db(async_session, data)
        except Exception as e:
            logger.error(f"Failed add_or_update_streamer_db: {e}")
            await session.rollback()


async def get_streamer_db(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            stmt = (
                select(Streamer)
                .where(Streamer.name.ilike(data.get('name')))
            )
            result = await session.execute(stmt)
            streamer = result.scalars().first
            if streamer:
                return {
                    "name": streamer.name,
                    "title": streamer.title,
                    "is_live": streamer.is_live,
                    "stream_id": streamer.stream_id,
                    "start_time": streamer.start_time,
                    "video_thumbnail": streamer.video_thumbnail,
                    "profile_pic": streamer.profile_pic,
                    "url": streamer.url
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Failed get_streamer_db: {e}")
            await session.rollback()


async def get_live_and_offline_streamers_db(
    async_session: async_sessionmaker
) -> tuple[list[dict], list[dict]]:
    live: list[dict] = []
    not_live: list[dict] = []
    async with async_session() as session:
        try:
            # Select * from streamer
            stmt = select(Streamer)
            result = await session.execute(stmt)
            streamers = result.all()
            for row in streamers:
                streamer_obj = row[0]
                if (streamer_obj.is_live):
                    data = {
                        "name": streamer_obj.name,
                        "start_time": streamer_obj.start_time,
                        "url": streamer_obj.url
                    }
                    live.append(data)
                else:
                    data = {
                        "name": streamer_obj.name,
                        "start_time": streamer_obj.start_time,
                        "url": streamer_obj.url
                    }
                    not_live.append(data)

            # sort treats as lowercase. without affecting original data
            live.sort(key=lambda v: v["name"].lower())
            not_live.sort(key=lambda v: v["name"].lower())

            return (live, not_live)
        except Exception as e:
            logger.error(f"Failed get_live_and_offline_streamers_db: {e}")
            await session.rollback()


async def get_is_live_status_db(async_session: async_sessionmaker, data: dict):
    async with async_session() as session:
        try:
            stmt = (
                select(Streamer)
                .where(Streamer.name.ilike(data.get('name')))
            )
            result = await session.execute(stmt)
            streamer = result.scalar()
            if streamer:
                return streamer.is_live
            else:
                return False
        except Exception as e:
            logger.error(f"Failed get_is_live_status_db: {e}")
            await session.rollback()


async def get_twitch_profile_pic(
    async_session: async_sessionmaker,
    data: dict
):
    async with async_session() as session:
        try:
            stmt = (
                select(Streamer)
                .where(Streamer.name.ilike(data.get('name')))
            )
            result = await session.execute(stmt)
            streamer = result.scalar()
            if streamer:
                return streamer.profile_pic
            else:
                return "N/A"
        except Exception as e:
            logger.error(f"Failed get twitch profile picture: {e}")
            await session.rollback()
