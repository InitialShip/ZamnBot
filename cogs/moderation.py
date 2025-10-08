import discord 
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Moderation Cog ready!")

    


async def setup(bot):
    await bot.add_cog(Moderation(bot))