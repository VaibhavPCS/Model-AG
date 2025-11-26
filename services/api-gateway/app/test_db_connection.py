"""
Test MySQL Database Connection
Run this to verify your database setup is correct.
"""

import asyncio
import aiomysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

async def test_connection():
    """Test the MySQL database connection."""
    
    config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'db': os.getenv('MYSQL_DATABASE', 'construction_monitoring'),
    }
    
    print("🔌 Testing MySQL connection...")
    print(f"Host: {config['host']}:{config['port']}")
    print(f"User: {config['user']}")
    print(f"Database: {config['db']}")
    print("-" * 50)
    
    try:
        # Create connection pool
        pool = await aiomysql.create_pool(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            db=config['db'],
            minsize=1,
            maxsize=5,
            echo=True
        )
        
        print("✅ Connection pool created successfully!")
        
        # Test query
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT VERSION()")
                result = await cursor.fetchone()
                print(f"✅ MySQL Version: {result[0]}")
                
                await cursor.execute("SELECT DATABASE()")
                result = await cursor.fetchone()
                print(f"✅ Current Database: {result[0]}")
                
                await cursor.execute("SHOW TABLES")
                tables = await cursor.fetchall()
                print(f"✅ Tables in database: {len(tables)}")
                if tables:
                    for table in tables:
                        print(f"   - {table[0]}")
                else:
                    print("   - (No tables yet - this is normal before migrations)")
        
        # Close pool
        pool.close()
        await pool.wait_closed()
        print("\n✅ Database connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database connection test FAILED!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if MySQL is running: brew services list")
        print("2. Verify database exists: mysql -u root -e 'SHOW DATABASES;'")
        print("3. Check .env file values match your MySQL setup")
        print("4. If using password, ensure it's correct")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
