import os
import asyncpg

_pool = None

async def get_db_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=5,
            command_timeout=60
        )
    return _pool

async def init_db():
    """Verify database connectivity only — schema is handled by 01_init.sql"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT current_database()")
        print(f"Connected to database: {result}")

async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None