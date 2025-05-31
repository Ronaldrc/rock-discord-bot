from db.db_init import (
    PlayerKill,
    Death,
)
from sqlalchemy import (
    update,
    select,
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from config.logger_config import get_logger
from datetime import datetime, timedelta
from db.pk import get_all_pk_sum_values_db
from db.death import get_all_death_sum_values_db

logger = get_logger(__name__)


async def get_all_profit_pk_sum_values_db(
    async_session: async_sessionmaker,
    time_range_hours: int = None
) -> str | None:
    """

    Parameter
    ----------
    async_session: async_sessionmaker
        
    
    time_range_hours: int
        In hours, retrieve data from now to time_range_hours hours ago.
        If None, sum all drops for all rsn

    Return a formatted string or "No content!".
    Names and values in descending order,
    sum of death value subtracted from the 
    sum of player kill estimated value for all rsn, in descending order
    """
    async with async_session() as session:
        pks = await get_all_pk_sum_values_db(
            async_session=async_session,
            time_range_hours=time_range_hours
        )
        pk_dict = dict(pks) if pks else {}

        deaths = await get_all_death_sum_values_db(
            async_session=async_session,
            time_range_hours=time_range_hours
        )
        death_dict = dict(deaths) if deaths else {}

    # Get all unique names from both lists
    all_names = set(pk_dict.keys()) | set(death_dict.keys())

    if all_names:
        all_names = set(pk_dict.keys()) | set(death_dict.keys())

        # Compute profit-pk values
        profit_pks = {name: pk_dict.get(name, 0) - death_dict.get(name, 0) for name in all_names}
        # print(f"pk_dict here:\n {pk_dict}")
        # print(f"death_dict here:\n {death_dict}")
        # print(f"profit_pks here:\n {profit_pks}")

        # Sort dictionary by values in descending order
        sorted_profit_pks = sorted(profit_pks.items(), key=lambda x: x[1], reverse=True)
        # print(f"sorted_profit_pks here:\n {sorted_profit_pks}")

        formatted_string = "".join(
            f"{i+1}) {name:<15}{int(value):,}\n" for i, (name, value) in enumerate(sorted_profit_pks)
        )

        return formatted_string

    return "No content!\n"
