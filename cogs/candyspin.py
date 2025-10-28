import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta

SPINS_PER_CYCLE = 5
RESET_HOURS = 8
WEEK_SECONDS = 7 * 24 * 3600
WEEKLY_ROLE_DURATION_DAYS = 6  

ROLES = {
    "participation": "🍭SweetLover",
    "top1_preweek": "🌟MineCandies",
    "top2_preweek": "✨CandyChaser",
    "top3_preweek": "🎉CandyThief",
    "top1_week": "🍬SugarPlum",
    "top2_week": "🍯HoneyBun",
    "top3_week": "🍫SweetTooth",
    "losers_week": "🍩LostCandy"
}

CANDY_ITEMS = [
    ("🍬 Candy", 5),
    ("🍭 Lollipop", 7),
    ("🍫 Chocolate", 10),
    ("🍩 Donut", 8),
    ("🍦 Ice Cream", 12),
    ("🍪 Cookie", 6),
    ("🍧 Shaved Ice", 9),
    ("🍰 Cupcake", 15),
    ("🍡 Dango", 11),
    ("🍯 Honey Candy", 20)
]

SPANK_GIFS = [
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTlrMmRsdTkyMGcyMmoxbTljOTM4M2ozeTdyZnY1eGttY2pmYnh6diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/miFItAUiTEHlaBrzGV/giphy.gif"
]

TWERK_GIFS = [
    "https://media2.giphy.com/media/egI6J8oXV2744CcOqP/giphy.gif",
]

KEKW_GIFS = [
    "https://media4.giphy.com/media/L3nWlmgyqCeU8/giphy.gif"
]


class CandySpin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_spin_channel = None  
        self.weekly_job_started = False

    async def ensure_table(self):
        """Ensure spins table exists (run once on ready)."""
        if not hasattr(self.bot, "db_pool") or self.bot.db_pool is None:
            print("CandySpin: db_pool not found on bot; table creation skipped.")
            return
        create_sql = """
        CREATE TABLE IF NOT EXISTS spins (
            user_id BIGINT PRIMARY KEY,
            total_points INTEGER DEFAULT 0,
            spins_used INTEGER DEFAULT 0,
            last_spin TIMESTAMP WITHOUT TIME ZONE DEFAULT '2000-01-01 00:00:00',
            weekly_points INTEGER DEFAULT 0
        );
        """
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(create_sql)

    async def fetch_user_row(self, user_id: int):
        async with self.bot.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM spins WHERE user_id = $1", user_id)
            return row

    async def ensure_user_row(self, user_id: int):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO spins (user_id, total_points, spins_used, last_spin, weekly_points) "
                "VALUES ($1, 0, 0, '2000-01-01 00:00:00', 0) ON CONFLICT (user_id) DO NOTHING", user_id
            )

    async def update_after_spin(self, user_id: int, pts: int, now: datetime):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE spins SET total_points = total_points + $1, weekly_points = weekly_points + $1, "
                "spins_used = spins_used + 1, last_spin = $2 WHERE user_id = $3",
                pts, now, user_id
            )

    async def reset_spins_if_needed(self, user_id: int, now: datetime):
        row = await self.fetch_user_row(user_id)
        if row is None:
            await self.ensure_user_row(user_id)
            return
        last = row["last_spin"] or datetime.utcnow() - timedelta(hours=RESET_HOURS + 1)
        if (now - last) >= timedelta(hours=RESET_HOURS) and row["spins_used"] > 0:
            async with self.bot.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE spins SET spins_used = 0 WHERE user_id = $1", user_id
                )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.ensure_table()
        if not self.weekly_job_started:
            self.weekly_announce.start()
            self.weekly_job_started = True
        print("CandySpin Cog ready.")

    @commands.command(name="spin")
    async def spin(self, ctx):
        """Spin the candy gacha (5 spins every 8 hours)."""
        user_id = ctx.author.id
        now = datetime.utcnow()

        await self.ensure_user_row(user_id)
        await self.reset_spins_if_needed(user_id, now)

        row = await self.fetch_user_row(user_id)
        spins_used = row["spins_used"]
        last_spin = row["last_spin"]

        if spins_used >= SPINS_PER_CYCLE:
            elapsed = (now - last_spin).total_seconds()
            remaining_seconds = RESET_HOURS * 3600 - elapsed
            if remaining_seconds < 0:
                remaining_seconds = 0
            hours, rem = divmod(int(remaining_seconds), 3600)
            minutes, seconds = divmod(rem, 60)
            await ctx.send(f"🍭 You’ve used all your spins! Next reset in **{hours}h {minutes}m {seconds}s**.")
            return

        item, pts = random.choice(CANDY_ITEMS)
        await self.update_after_spin(user_id, pts, now)

        participation_name = ROLES.get("participation")
        if participation_name:
            role = discord.utils.get(ctx.guild.roles, name=participation_name)
            if role and role not in ctx.author.roles:
                try:
                    await ctx.author.add_roles(role)
                except Exception:
                    pass  

        self._last_spin_channel = ctx.channel

        row_after = await self.fetch_user_row(user_id)
        used = row_after["spins_used"]
        embed = discord.Embed(
            description=f"🎉 {ctx.author.mention} spun and got **{item}** worth **{pts} points!**\n({used}/{SPINS_PER_CYCLE} spins used)",
            color=0xFFB6C1
        )
        embed.set_author(name=f"{ctx.author.display_name}'s Candy Pull")
        await ctx.send(embed=embed)

    @commands.command(name="rank")
    async def rank(self, ctx):
        """Show top 10 candy collectors by total_points."""
        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id, total_points FROM spins ORDER BY total_points DESC LIMIT 10")
        if not rows:
            await ctx.send("No candy points yet — go spin with spin🍭")
            return

        msg = "**🍭 Candy Leaderboard — Top 10**\n"
        for i, r in enumerate(rows, start=1):
            uid = r["user_id"]
            points = r["total_points"]
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"<@{uid}>"
            msg += f"{i}. {name} — {points} pts\n"
        await ctx.send(msg)

    @tasks.loop(seconds=WEEK_SECONDS)
    async def weekly_announce(self):
        """Announce weekly top 3 and reset weekly_points (runs every 7 days)."""
        channel = self._last_spin_channel
        if channel is None:
            print("CandySpin: no recent spin channel stored; weekly announcement skipped.")
            return

        async with self.bot.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id, weekly_points FROM spins ORDER BY weekly_points DESC LIMIT 3")
        if not rows:
            await channel.send("No spins this week — no Candy winners! 🍭")
            return

        desc_lines = []
        winners = []
        for i, r in enumerate(rows, start=1):
            uid = r["user_id"]
            pts = r["weekly_points"]
            member = channel.guild.get_member(uid) 
            mention = member.mention if member else f"<@{uid}>"
            desc_lines.append(f"{i}. {mention} — {pts} pts")
            winners.append((uid, member))

        embed = discord.Embed(
            title="🏆 Weekly Candy Winners!",
            description="\n".join(desc_lines),
            color=0xFFD700
        )
        announce_msg = await channel.send(embed=embed)

        role_keys = ["top1_week", "top2_week", "top3_week"]
        for idx, (uid, member) in enumerate(winners):
            role_name = ROLES.get(role_keys[idx])
            if role_name and member:
                guild = channel.guild
                role = discord.utils.get(guild.roles, name=role_name)
                if role is None:
                    try:
                        role = await guild.create_role(name=role_name, reason="Weekly candy winner role auto-created")
                    except Exception as e:
                        print(f"Failed to create role {role_name}: {e}")
                        role = None
                if role:
                    try:
                        await member.add_roles(role)
                        asyncio.create_task(self._remove_role_after_delay(member, role, WEEKLY_ROLE_DURATION_DAYS * 24 * 3600))
                    except Exception as e:
                        print(f"Failed to add role {role_name} to {member}: {e}")

        wing_uids = {uid for uid, _ in winners}
        async with self.bot.db_pool.acquire() as conn:
            participants = await conn.fetch("SELECT user_id FROM spins WHERE weekly_points > 0")
        losers_role_name = ROLES.get("losers_week")
        losers_role = None
        if losers_role_name:
            losers_role = discord.utils.get(channel.guild.roles, name=losers_role_name)
            if losers_role is None:
                try:
                    losers_role = await channel.guild.create_role(name=losers_role_name)
                except Exception:
                    losers_role = None
        for row in participants:
            uid = row["user_id"]
            if uid not in wing_uids:
                member = channel.guild.get_member(uid)
                if member and losers_role:
                    try:
                        await member.add_roles(losers_role)
                        asyncio.create_task(self._remove_role_after_delay(member, losers_role, WEEKLY_ROLE_DURATION_DAYS * 24 * 3600))
                    except Exception:
                        pass

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("UPDATE spins SET weekly_points = 0")

    async def _remove_role_after_delay(self, member: discord.Member, role: discord.Role, delay_seconds: int):
        try:
            await asyncio.sleep(delay_seconds)
            guild = member.guild
            m = guild.get_member(member.id)
            if m and role in m.roles:
                try:
                    await m.remove_roles(role)
                except Exception:
                    pass
        except Exception:
            pass

    @commands.command(name="slap")
    async def slap(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("Slap Time Muhehehe!")
        gif = random.choice(SPANK_GIFS)
        embed = discord.Embed(title=f"👋 {ctx.author.display_name} slaps {member.display_name}!", color=0xFF69B4)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @commands.command(name="twerk")
    async def twerk(self, ctx, member: discord.Member = None):
        gif = random.choice(TWERK_GIFS)
        if member:
            desc = f"🛸 Alien twerks on {member.mention}!"
        else:
            desc = "🛸 Alien twerk invasion!"
        embed = discord.Embed(title="Alien Attack!", description=desc, color=0xFFD700)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

    @commands.command(name="kekw")
    async def kekw(self, ctx):
        gif = random.choice(KEKW_GIFS)
        embed = discord.Embed(title="KEKW", color=0xFF4500)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CandySpin(bot))
