import asyncio
import databases

# Replace this with your actual Supabase DATABASE_URL
DATABASE_URL = "postgresql+asyncpg://postgres.yyiguvuujvsnetkgothl:readauraadmin28@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

# Create the database object
database = databases.Database(DATABASE_URL)

async def test_connection():
    try:
        await database.connect()
        print("✅ Connection successful!")
    except Exception as e:
        print("❌ Connection failed:", e)
    finally:
        await database.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())
