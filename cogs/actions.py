import discord 
from discord.ext import commands
import random
from discord import app_commands

SPANK_GIF_URL = ["https://cdn.discordapp.com/attachments/1422926133250359347/1431559863221223495/image0.gif?ex=68fddb84&is=68fc8a04&hm=b24b878e705d9df151d93595deb427ecaaab51397c670e5f98884d677b6cfcec&",
           "https://cdn.discordapp.com/attachments/1422926133250359347/1431559928451039323/image0.gif?ex=68fddb94&is=68fc8a14&hm=4e4a2e84d211a1312c963a13e46c0366c937b1f11074c07fbe53c63a3057d826&",
           "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTlrMmRsdTkyMGcyMmoxbTljOTM4M2ozeTdyZnY1eGttY2pmYnh6diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/miFItAUiTEHlaBrzGV/giphy.gif",
           ]

TWERK_GIFS = [
    "https://media2.giphy.com/media/egI6J8oXV2744CcOqP/giphy.gif",
]

KEKW_GIFS = [
    "https://media4.giphy.com/media/L3nWlmgyqCeU8/giphy.gif",
]

class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Fun Cog ready!")

    @commands.command(name="spank")
    async def spank(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(
            color=discord.Color.blue()
        )
        embed.set_author(name=f"{ctx.author.display_name} spanks {member.display_name}!", icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=random.choice(SPANK_GIF_URL))
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
    await bot.add_cog(Actions(bot))