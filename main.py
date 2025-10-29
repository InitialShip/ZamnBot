# main.py
import os
import logging as log
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncpg as acpg

from core.keep_alive import keep_alive
from core.databasehandler import DatabaseHandler
from core.cog_loader import load_all_cogs
from core import queries


# ============================================================
# Load environment variables
# ============================================================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "z!")
IS_DEVELOPMENT = os.getenv("IS_DEVELOPMENT", "false").lower() == "true"
DB_URL = os.getenv("DATABASE_URL")


# ============================================================
# Discord Intents
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


# ============================================================
# Bot Class Definition
# ============================================================
class BotRunner(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_pool: acpg.Pool | None = None
        self.db_handler: DatabaseHandler | None = None

    async def setup_hook(self):
        """Executed before bot connects to Discord."""
        try:
            print("🔌 Connecting to PostgreSQL database...")
            self.db_pool = await acpg.create_pool(DB_URL)

            # Run table creation query from queries.py
            await self.db_pool.execute(queries.CREATE_USERS_TABLE)

            self.db_handler = DatabaseHandler(self.db_pool)
            print("✅ Database ready.")
        except Exception as e:
            print(f"❌ Failed to connect database: {e}")

        # --- Load all cogs ---
        print("🧩 Loading cogs...")
        await load_all_cogs(self)
        await self.tree.sync()
        print("✅ All cogs loaded successfully.")

    async def on_ready(self):
        print(f"🚀 Logged in as {self.user.name}")
        await self.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help | 💣"))


# ============================================================
# Bot Initialization
# ============================================================
bot = BotRunner(command_prefix=COMMAND_PREFIX, intents=intents)


# ============================================================
# Bot Runner
# ============================================================
if __name__ == "__main__":
    if IS_DEVELOPMENT:
        handler = log.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
        bot.run(token=TOKEN, log_handler=handler, log_level=log.DEBUG)
    else:
        keep_alive()
        bot.run(token=TOKEN)
