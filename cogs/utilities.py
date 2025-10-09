import discord 
from discord.ext import commands
import random

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Fun Cog ready!")

    @commands.command()
    async def poll(ctx, *,title , question):
        embed = discord.Embed(title=title, description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Utilities(bot))