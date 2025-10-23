from typing import Optional, List, Any
import asyncpg as acpg
import datetime
import math


class DatabaseHandler:
    def __init__(self, pool:acpg.Pool):
        self.pool = pool

    async def execute(self, query: str, *args):
        return await self.pool.execute(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        return await self.pool.fetchval(query,*args)
    
    async def fetchrow(self, query: str, *args) -> Optional[acpg.Record]:
        return await self.pool.fetchrow(query, *args)
    
    async def get_user_balance(self, user_id) -> List[acpg.Record]:
        await self.pool.execute(
                    "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", 
                    user_id)
        
        record = await self.pool.fetchrow(
            "SELECT points, daily_count FROM users WHERE user_id = $1",
            user_id)
        return record
    
    async def get_user_streak_count(self, user_id) -> int:
        await self.pool.execute(
                    "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", 
                    user_id)
        query = "SELECT daily_count FROM users WHERE user_id = $1"
        return await self.pool.fetchval(query,user_id)
    
    async def add_points(self, user_id: int, amount: int) -> int:
        new_balance = await self.pool.fetchval(
            "UPDATE users SET points = points + $2 WHERE user_id = $1 RETURNING points",
            user_id
            ,amount)
        return new_balance

    async def process_daily_claim(self, user_id, daily_amount: int, interest_rate: float, cooldown: int) -> tuple[bool, int]:
        current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        try:
            async with self.pool.acquire() as conn:
                conn: acpg.Connection
                await conn.execute(
                    "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", 
                    user_id)
                
                claim_record = await conn.fetchrow(
                        "SELECT daily_count, last_daily FROM users WHERE user_id = $1",
                        user_id
                    )
                time_since_last_claim = current_time - claim_record['last_daily']
                seconds_remaining = cooldown - time_since_last_claim.total_seconds()
                if seconds_remaining > 0:
                    return False, 0, 0, 0, seconds_remaining

                daily_bonus = round(daily_amount*math.pow((1 + interest_rate),claim_record['daily_count']))

                new_balance = await conn.fetchval(
                    "UPDATE users SET points = points + $2, last_daily = $3, daily_count = daily_count + 1 WHERE user_id = $1 RETURNING points",
                    user_id,
                    daily_bonus,
                    current_time)
                
                return True, daily_bonus, new_balance, claim_record['daily_count'], None
        except Exception as e:
            return (False, )
                
    async def transfer_point(self, src_user_id: int, end_user_id: int, amount:int) -> None:
        pass

    async def reconnect(self) -> bool:
        pass