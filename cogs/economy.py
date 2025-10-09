import discord 
from discord.ext import commands
import random
import asyncpg as acpg
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
SLOTS_SYMBOLS = ["🍒", "🍇", "🍊", "🍋", "💰", "💎"]
WIN_MULTIPLIER = 5

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None
        print("Economy Cog ready!")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.pool is not None:
            return
        
        print("Connecting to database.")
        try:
            self.pool = await acpg.create_pool(db_url)
            await self.pool.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    points INTEGER DEFAULT 0
                )
            ''')
            print("PostgreSQL connection pool established and table checked.")
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")

    async def get_user_balance(self, user_id):
        await self.pool.execute (
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", user_id
        )
        points = await self.pool.fetchval(
            "SELECT points FROM users WHERE user_id = $1", 
            user_id
        )
        return points

    @commands.command(name='balance', aliases=['b','bl'])
    async def balance(self, ctx):
        target = ctx.author
        user_id = target.id
        try:
            balance = await self.get_user_balance(user_id=user_id)
        except Exception as e: 
            print(f"Error while getting user balance with id {user_id} : {e}")
            return await ctx.reply("There was a problem can not get your balance")
        
        embed = discord.Embed(
            title="💰 Balance",
            color=discord.Color.blue()
        )
        
        # Set the thumbnail to the target user's avatar
        if ctx.author.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        if target == ctx.author:
            embed.description = f"**{target.display_name}**, your current balance is:"
            embed.add_field(name="Current Points", value=f"**{balance:,}** points", inline=False)
        else:
            embed.description = f"**{target.display_name}**'s current balance is:"
            embed.add_field(name="Current Points", value=f"**{balance:,}** points", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='slots', aliases=['sl'])
    async def slots(self, ctx):
        results = [random.choice(SLOTS_SYMBOLS) for _ in range(3)]
        display_results = f"|{'|'.join(results)}|"

        if results[0] == results[1] == results [2]:
            winnings = 100 * WIN_MULTIPLIER
            message = (
                f"**🎰 SLOT MACHINE SPIN 🎰**\n\n"
                f"**{display_results}**\n\n"
                f"🎉 **JACKPOT!** {results[0]}x3! You won {winnings} points! 🎉"
            )
        else:
            message = (
                f"**🎰 SLOT MACHINE SPIN 🎰**\n\n"
                f"**{display_results}**\n\n"
                f"Try again next time! Better luck soon. 💔"
            )

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Economy(bot))