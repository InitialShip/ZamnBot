import discord 
from discord.ext import commands
import random

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Fun Cog ready!")

    @commands.hybrid_command(name = "avatar", aliases=["a"], description="Display your avatar")
    async def  get_avatar(self, ctx:commands.Context, member: discord.Member = None):
        target = member or ctx.author

        embed = discord.Embed(
            title= f"@{target.display_name}'s Avatar",
            color=discord.Color.dark_blue()
        )
        embed.set_image(url=target.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @commands.command()
    async def poll(ctx, *,title , question):
        embed = discord.Embed(title=title, description=question)
        poll_message = await ctx.send(embed=embed)
        await poll_message.add_reaction("👍")
        await poll_message.add_reaction("👎")

async def setup(bot):
    await bot.add_cog(Utilities(bot))