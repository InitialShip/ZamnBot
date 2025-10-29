import discord
from discord.ext import commands
import asyncpg as acpg
from dotenv import load_dotenv
from core.databasehandler import DatabaseHandler
import datetime


class Memetics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.pool: acpg.Pool = self.bot.db_pool
        self.handler: DatabaseHandler = self.bot.db_handler

    @commands.hybrid_command(name="showmemetics")
    async def show_memetics(self, ctx: commands.Context):
        embed = discord.Embed(title="Memetics", color=discord.Color.blue())
        records = await self.handler.get_memetics()
        for r in records:
            embed.add_field(
                name=f"{r['name']} {r['icon']}", value=r["description"], inline=False
            )
        embed.set_author(
            name=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Memetics(bot))
