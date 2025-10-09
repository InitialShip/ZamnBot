import discord 
from discord.ext import commands
import random
import asyncpg as acpg
import os
from dotenv import load_dotenv
import datetime

load_dotenv()
db_url = os.getenv('DATABASE_URL')
SLOTS_SYMBOLS = ["🍒", "🍇", "🍊", "🍋", "💰", "💎"]
WIN_MULTIPLIER = 5
COOLDOWN_SECONDS = 8 * 60 * 60 #8 hours
DAILY_REWARD = 500

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
                    points INTEGER DEFAULT 0,
                    last_daily TIMESTAMP WITHOUT TIME ZONE DEFAULT '2000-01-01 00:00:00'
                )
            ''')
            print("PostgreSQL connection pool established and table checked.")
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")

    async def create_user_if_not_exist(self, user_id):
        await self.pool.execute(
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING", user_id
        )

    async def get_user_balance(self, user_id):
        await self.create_user_if_not_exist()

        points = await self.pool.fetchval(
            "SELECT points FROM users WHERE user_id = $1", 
            user_id
        )
        return points
    
    async def give_user_balance(self, user_id, amount) -> int:
        await self.create_user_if_not_exist()

        new_points = await self.pool.fetchval(
            "UPDATE users SET points = points + $2 WHERE user_id = $1 RETURNING points",
            user_id,
            amount
        )
        return new_points

    @commands.command(name = "daily", aliases=["claim"])
    async def  daily(self, ctx:commands.Context):
        user_id = ctx.author.id
        current_time = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        try:
            async with self.pool.acquire() as conn:
                last_daily = await conn.fetchval(
                    "SELECT last_daily FROM users WHERE user_id = $1",
                    user_id
                )
                time_since_last_claim = current_time - last_daily
                seconds_remaining = COOLDOWN_SECONDS - time_since_last_claim.total_seconds()
                if seconds_remaining > 0:
                    minutes, seconds = divmod(seconds_remaining, 60)
                    hours, minutes = divmod(minutes, 60)
                
                    return await ctx.send(
                        f"⏰ You are on cooldown! Claim your next daily in "
                        f"**{int(hours)}h {int(minutes)}m {int(seconds)}s**."
                    )
                
                new_balance = await conn.fetchval(
                    "UPDATE users SET points = points + $2, last_daily = $3 WHERE user_id = $1 RETURNING points",
                    user_id,
                    DAILY_REWARD,
                    current_time  # Save the current time (UTC)
                )
                embed = discord.Embed(
                title="🎁 Daily Reward Claimed!",
                description=f"You received **{DAILY_REWARD:,}** points.",
                color=discord.Color.gold()
                )
                embed.set_footer(text=f"Your new balance is: {new_balance:,} points")
                await ctx.send(embed=embed)
        except Exception as e:
            print(f"Daily command error for {ctx.author.id}: {e}")
            await ctx.send("An error occurred while processing your claim.")

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
        
        if ctx.author.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        if target == ctx.author:
            embed.description = f"**{target.display_name}**, your current balance is:"
            embed.add_field(name="Current Points", value=f"**{balance:,}** points", inline=False)
        else:
            embed.description = f"**{target.display_name}**'s current balance is:"
            embed.add_field(name="Current Points", value=f"**{balance:,}** points", inline=False)

        await ctx.send(embed=embed)

    # @commands.command(name = "sharecredits", aliases=["sc"])
    # async def  share_credits(self, ctx:commands.Context, member: discord.member):
    #     await ctx.send("This command is for sharing credits")

    @commands.command(name = "givecredits")
    @commands.is_owner()
    async def give_balance(self, ctx,member: discord.Member, amount: int):
        if amount <= 0:
            return ctx.send("Amount must be a number")
        
        target = member
        user_id = target.id
        try:
            new_balance = await self.give_user_balance(user_id=user_id,amount=amount)
        except Exception as e:
            print(f"Error while giving user balance with id {user_id} : {e}")
            return await ctx.reply("There was a problem")
        await ctx.send(f"Gave {member.display_name} {amount} credits! New Balance: {new_balance}")

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

    # @commands.command(name = "roulette")
    # async def  roulette(self, ctx:commands.Context):
    #     await ctx.send("template command")

async def setup(bot):
    await bot.add_cog(Economy(bot))