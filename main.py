import discord
from discord.ext import commands
import logging as log
from dotenv import load_dotenv
import os
from keep_alive import keep_alive

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
keep_alive()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

COMMAND_PREFIX = 't!'

INITIAL_COGS = [
    'cogs.fun',
    'cogs.moderation',
    'cogs.utilities',
    'cogs.economy'
]


class ZamnBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        print("Running setup_hook: Loading Cogs...")
        await self.load_cogs()
    print("Cogs loaded. Connecting to Discord...")
    async def load_cogs(self):
        for extension_name in INITIAL_COGS:
            try:
                await self.load_extension(extension_name)
                print(f'Successfully loaded extension: {extension_name}')
            except Exception as e:
                print(f'Failed to load extension {extension_name}. Reason: {e}')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Zamn ! We are ready to go in, {self.user.name}")
        await self.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help | 💣"))


bot = ZamnBot(COMMAND_PREFIX, intents=intents)

@bot.command(name="reload", aliases=['r'])    
@commands.is_owner()
async def reload(ctx, extension_name: str):
    if extension_name is None:
        return
    module_path = f'cogs.{extension_name}'
    try:
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


bot.run(token)
