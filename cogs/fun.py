import discord
from discord.ext import commands
import random
from discord import app_commands


MESSAGES_LIMIT = 1000  # human messages
SPANK_GIF_URL = [
    "https://cdn.discordapp.com/attachments/1422926133250359347/1431559863221223495/image0.gif?ex=68fddb84&is=68fc8a04&hm=b24b878e705d9df151d93595deb427ecaaab51397c670e5f98884d677b6cfcec&",
    "https://cdn.discordapp.com/attachments/1422926133250359347/1431559928451039323/image0.gif?ex=68fddb94&is=68fc8a14&hm=4e4a2e84d211a1312c963a13e46c0366c937b1f11074c07fbe53c63a3057d826&",
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send(f"Hello, {ctx.author.display_name} <:xdd:1425172451150659727>")

    @commands.command(name="cat")
    async def cat(self, ctx):
        await ctx.reply(
            "https://tenor.com/view/bobitos-mimis-michis-gif-943529865427663588"
        )

    @commands.command(name="spank")
    async def spank(self, ctx: commands.Context, member: discord.Member):
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(
            name=f"{ctx.author.display_name} spanks {member.display_name}!",
            icon_url=ctx.author.display_avatar.url,
        )
        embed.set_image(url=random.choice(SPANK_GIF_URL))
        await ctx.send(embed=embed)

    @commands.command(name="zamn", aliases=["countzamn", "zamnscan"])
    async def zamn(self, ctx):
        await ctx.send(
            "Starting message scan in this channel for [zamn]... This may take a moment."
        )
        zamn_authors = {}
        zamn_count = 0
        total_messages = 0

        prefix = self.bot.command_prefix
        async for message in ctx.channel.history(limit=None):
            if message.author.bot:
                continue
            if message.content.startswith(prefix):
                continue
            if "zamn" in message.content.lower():
                # print(f"zamn found in message ID {message.id} from {message.author}")
                author_name = message.author.display_name
                zamn_authors[author_name] = zamn_authors.get(author_name, 0) + 1
                zamn_count += 1

            total_messages += 1
            if total_messages >= MESSAGES_LIMIT:
                break

        if not zamn_authors:
            report = (
                f">>>**Zamn Count Complete**\n"
                f"Processed **{total_messages}** messages.\n"
                f"Found **0** user messages containing the word [zamn]."
            )
        else:
            sorted_authors = sorted(
                zamn_authors.items(), key=lambda item: item[1], reverse=True
            )
            top_list = "".join(
                [f"`{name}`: {count} messages.\n" for name, count in sorted_authors[:5]]
            )

            report = (
                f">>> **Zamn Count Complete**\n"
                f"Processed **{total_messages}** messages.\n"
                f"Total [zamn] messages found: **{zamn_count}**.\n"
                f"**Top 5 Zamner:**\n{top_list}"
            )

        await ctx.send(report)

    @commands.command(name="scan")
    async def scan_for_word(self, ctx, word: str):
        await ctx.send(
            f"Starting message scan in this channel for [**{word}**]... This may take a moment."
        )

        prefix = self.bot.command_prefix
        authors = {}
        count = 0
        total_messages = 0
        async for message in ctx.channel.history(limit=None):
            if message.author.bot:
                continue
            if message.content.startswith(prefix):
                continue
            if word.lower() in message.content.lower():
                print(f"found in message ID {message.id} from {message.author}")
                author_name = message.author.display_name
                authors[author_name] = authors.get(author_name, 0) + 1
                count += 1

            total_messages += 1
            if total_messages >= MESSAGES_LIMIT:
                break

        if not authors:
            report = (
                f">>> **[**{word}**] Count Complete**\n"
                f"Processed **{total_messages}** messages.\n"
                f"Found **0** user messages containing the word [**{word}**]."
            )
        else:
            sorted_authors = sorted(
                authors.items(), key=lambda item: item[1], reverse=True
            )
            top_list = "".join(
                [f"`{name}`: {count} messages.\n" for name, count in sorted_authors[:5]]
            )
            report = (
                f">>> **[**{word}**] Count Complete**\n"
                f"Processed **{total_messages}** messages.\n"
                f"Total [**{word}**] messages found: **{count}**.\n"
                f"**Top 5 :**\n{top_list}"
            )
        await ctx.send(report)

    @scan_for_word.error
    async def scan_for_word_error(self, ctx, error):
        prefix = self.bot.command_prefix
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage: {prefix}scan <word>")


async def setup(bot):
    await bot.add_cog(Fun(bot))
