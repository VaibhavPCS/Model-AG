"""
Database Session Management
Purpose: Async MySQL session handling
Author: BMAD BMM Agents Dev
Date: 2025-11-26
"""

import aiomysql
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.db.base import Base

# Database connection pool (aiomysql)
db_pool = None

# SQLAlchemy async engine (for migrations and ORM)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db_pool():
    """Initialize database connection pool."""
    global db_pool
    try:
        db_pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DATABASE,
            minsize=1,
            maxsize=10,
            autocommit=False
        )
        print(f"✅ Database pool created successfully")
    except Exception as e:
        print(f"❌ Failed to create database pool: {str(e)}")


async def close_db_pool():
    """Close database connection pool."""
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
        print("✅ Database pool closed")


async def get_db():
    """
    Dependency for getting async database sessions.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """
    Check if database connection is working using aiomysql directly.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Create a test connection
        conn = await aiomysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DATABASE
        )
        
        # Test query
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT VERSION() as version, DATABASE() as db")
            result = await cursor.fetchone()
            
            if result:
                print(f"✅ Database connection successful!")
                print(f"   MySQL Version: {result[0]}")
                print(f"   Database: {result[1]}")
                conn.close()
                return True
            else:
                print("❌ Query returned no results")
                conn.close()
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False
