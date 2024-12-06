from sqlalchemy import Column, Integer, String, DateTime, Boolean, update, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from dotenv import load_dotenv
import os
import json
import asyncio
from logger_config import get_logger
from rich import print

logger = get_logger(__name__)

load_dotenv(".env")
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
Base = declarative_base()
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Streamer(Base):
    __tablename__ = 'streamer'
    name = Column(String(40), primary_key=True, nullable=False)
    title = Column(String(255), server_default="N/A")
    is_live = Column(Boolean, default=False)
    stream_id = Column(Integer, default=-1)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    video_thumbnail = Column(String(200), server_default="N/A")
    profile_pic = Column(String(200), server_default="N/A")
    url = Column(String(60), server_default="N/A")

# Create table if not exist
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_streamer_db(async_session : async_sessionmaker, data : json):
    try:
        logger.info(f"Adding {data.get('name', "")} to db")
        async with async_session() as session:
            new_streamer = Streamer(
                name= data.get('name'),
                title= data.get('title', "N/A"),
                is_live= data.get('is_live', False),      # livestream id is used to get video_thumbnail
                stream_id = data.get('stream_id', -1),
                video_thumbnail = data.get("video_thumbnail", "N/A"),
                profile_pic = data.get('profile_pic', "N/A"),
                url = data.get('url', "N/A")
            )
            session.add(new_streamer)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed adding {data.get('name', "")} to db: {e}")
        await session.rollback()

async def update_streamer_db(async_session : async_sessionmaker, data : json):
    try:
        logger.info(f"Updating {data.get('name', "")} to db")
        async with async_session() as session:
            stmt = (
                update(Streamer)
                .where(Streamer.name == data['name'])
                .values(**data)
            )
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        logger.error(f"Failed updating {data.get('name', "")} to db: {e}")
        await session.rollback()

# Add if new entry, else update
async def add_or_update_streamer_db(async_session : async_sessionmaker, data : json):
    try:
        async with async_session() as session:
            stmt = select(Streamer).where(Streamer.name == data.get('name'))
            result = await session.execute(stmt)
            streamer = result.scalar()
        if streamer:
            await update_streamer_db(async_session, data)
        else:
            await add_streamer_db(async_session, data)
    except Exception as e:
        logger.error(f"Failed add_or_update_streamer_db: {e}")

async def get_streamer_db(async_session : async_sessionmaker, data : json):
    try:
        async with async_session() as session:
            stmt = select(Streamer).where(Streamer.name == data.get('name'))
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
                "url" : streamer.url
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Failed get_streamer_db: {e}")

async def get_live_and_offline_streamers_db() -> tuple[dict, dict]:
    live: list[tuple] = []
    not_live: list[tuple] = []
    try:
        # Select * from streamer
        async with async_session() as session:
            stmt = select(Streamer)
            result = await session.execute(stmt)
            streamers = result.all()
            for row in streamers:
                streamer_obj = row[0]
                if (streamer_obj.is_live == True):
                    live.append((streamer_obj.name, streamer_obj.url))
                else:
                    not_live.append((streamer_obj.name, streamer_obj.url))

        # sort by treating all letters as lowercase, without affecting original data
        live.sort(key = lambda v: v[0].lower())
        not_live.sort(key = lambda v: v[0].lower())

        return (live, not_live)
    except Exception as e:
        logger.error(f"Failed get_live_and_offline_streamers_db: {e}")

async def get_is_live_status_db(async_session : async_sessionmaker, data : json):
    try:
        async with async_session() as session:
            stmt = select(Streamer).where(Streamer.name == data.get('name'))
            result = await session.execute(stmt)
            streamer = result.scalar()
        if streamer:
            return streamer.is_live
        else:
            return False
    except Exception as e:
        logger.error(f"Failed get_is_live_status_db: {e}")

async def get_twitch_profile_pic(async_session : async_sessionmaker, data : json):
    try:
        async with async_session() as session:
            stmt = select(Streamer).where(Streamer.name == data.get('name'))
            result = await session.execute(stmt)
            streamer = result.scalar()
        if streamer:
            return streamer.profile_pic
        else:
            return "N/A"
    except Exception as e:
        logger.error(f"Failed get twitch profile picture: {e}")

if __name__ == '__main__':
    # example data
    data = {
        "name" : "steamykakes",
        "title" : "casual Saturday gaming",
        "is_live" : True,
        "stream_id" : 42110532,
        "video_thumbnail" : "https://stream.kick.com/thumbnails/livestream/42110532/thumb0/video_thumbnail/thumb0.jpg",
        "profile_pic" : "https://files.kick.com/images/user/2401237/profile_image/conversion/2e32dacf-d3a4-4755-8b34-340a957f528a-fullsize.webp",
    }
    # add_streamer_to_db(async_session, data)
    # asyncio.run(create_tables())
    # asyncio.run(test_connection())
    # asyncio.run(add_streamer_db(async_session, data))
    # asyncio.run(update_streamer_db(async_session, data))
    # asyncio.run(add_or_update_streamer_db(async_session, data))
    asyncio.run(get_is_live_status_db(async_session, data))