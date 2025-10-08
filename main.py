import discord
from discord.ext import commands
import logging as log
from dotenv import load_dotenv
import os
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

keep_alive()

handler = log.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

COMMAND_PREFIX = 'z!'


INITIAL_COGS = [
    'cogs.fun',
    'cogs.moderation'
]

bot = commands.Bot(COMMAND_PREFIX, intents=intents)


async def load_cogs():
    for extension_name in INITIAL_COGS:
        try:
            await bot.load_extension(extension_name)
            print(f'Successfully loaded extension: {extension_name}')
        except Exception as e:
            print(f'Failed to load extension {extension_name}. Reason: {e}')

zamn_count = 0

@bot.event
async def on_ready():
    print(f"Zamn ! We are ready to go in, {bot.user.name}")

    await load_cogs() 
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help | 💣"))

@commands.is_owner()
@bot.command(name="reload")
async def reload(ctx, extension_name: str):
    if extension_name is None:
        return
    module_path = f'cogs.{extension_name}'
    try:
        # discord.py has a built-in reload_extension method for convenience
        await bot.reload_extension(module_path)
        await ctx.send(f"Successfully reloaded: `{extension_name}`")
    except commands.ExtensionNotLoaded:
        await ctx.send(f"`{extension_name}` is not loaded. Attempting to load instead...")
        await bot.load_extension(module_path)
        await ctx.send(f"Successfully loaded: `{extension_name}` instead of reloading.")
    except Exception as e:
        await ctx.send(f"Failed to reload `{extension_name}`. Error: {e}")

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Usage: {COMMAND_PREFIX}reload <module_name>")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")


# @bot.command()
# async def poll(ctx, *, question):
#     embed = discord.Embed(title="New Poll", description=question)
#     poll_message = await ctx.send(embed=embed)
#     await poll_message.add_reaction("👍")
#     await poll_message.add_reaction("👎")

bot.run(token, log_handler=handler, log_level=log.DEBUG)