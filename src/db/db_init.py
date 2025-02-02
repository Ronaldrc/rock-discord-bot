from sqlalchemy import (
    Column,
    Integer,
    Float,
    BigInteger,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.sql.functions import sum
from dotenv import load_dotenv
import os
from config.logger_config import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(
    url=DATABASE_URL,
    pool_pre_ping=True
)
Base = declarative_base()
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Streamer(Base):
    __tablename__ = 'streamer_test'
    name = Column(String(40), primary_key=True, nullable=False)
    title = Column(String(255), server_default="N/A")
    is_live = Column(Boolean, default=False)
    stream_id = Column(Integer, default=-1)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    video_thumbnail = Column(String(200), server_default="N/A")
    profile_pic = Column(String(200), server_default="N/A")
    url = Column(String(60), server_default="N/A")


class PersonalBest(Base):
    __tablename__ = 'personal_best_test'
    id = Column(Integer, primary_key=True)
    rsn = Column(String(15))
    date = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float)


class Drop(Base):
    __tablename__ = 'drop_test'
    id = Column(Integer, primary_key=True)
    rsn = Column(String(15))
    date = Column(DateTime(timezone=True), server_default=func.now())
    item = Column(String(40))
    loot_big_int = Column(BigInteger)
    loot_string = Column(String(22))    # number with commas


class Death(Base):
    __tablename__ = 'death_test'
    id = Column(Integer, primary_key=True)
    rsn = Column(String(15))
    date = Column(DateTime(timezone=True), server_default=func.now())
    loot_big_int = Column(BigInteger)
    loot_string = Column(String(22))    # number with commas


class PlayerKill(Base):
    __tablename__ = 'player_kill_test'
    id = Column(Integer, primary_key=True)
    rsn = Column(String(15))
    date = Column(DateTime(timezone=True), server_default=func.now())
    loot_big_int = Column(BigInteger)
    loot_string = Column(String(22))    # number with commas


# Create table if not exist
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    # example data
    data = {
        "name": "steamykakes",
        "title": "casual Saturday gaming",
        "is_live": True,
        "stream_id": 42110532,
        "video_thumbnail": ("https://stream.kick.com/thumbnails/livestream/"
                            "42110532/thumb0/video_thumbnail/thumb0.jpg"),
        "profile_pic": ("https://files.kick.com/images/user/2401237/"
                        "profile_image/conversion/2e32dacf-d3a4-4755-"
                        "8b34-340a957f528a-fullsize.webp"),
    }
    # add_streamer_to_db(async_session, data)
    # asyncio.run(create_tables())
    # asyncio.run(test_connection())
