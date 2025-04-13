"""
IgnisBot Main Module
Author: Isaiah Jared (2019)
"""
import datetime
from datetime import datetime
import os
import discord
from discord.ext import commands
import toml

config = toml.load("config.toml")

API_TOKEN = config["API_TOKEN"]
COMMAND_PREFIX = config["COMMAND_PREFIX"]
OWNER_ID = config["OWNER_ID"]
BOT_STATUS_MSG = config["BOT_STATUS_MSG"]
COGS_DIR = config["COGS_DIR"]

bot = commands.Bot(
  command_prefix=COMMAND_PREFIX, 
  case_insensitive=True, 
  owner_id=OWNER_ID, 
  intents=discord.Intents.all()
  )


bot.remove_command('help') # Defining our own help cmd in utility commands, leave this in place.

@bot.event
async def on_ready():
  now_ready = datetime.now()
  dt_str_ready = now_ready.strftime("%m/%d/%Y %H:%M:%S")
  print(f"Ignis Bot ::::: ONLINE\n\n{dt_str_ready}")
  await bot.change_presence(activity=discord.Game(name=BOT_STATUS_MSG))

@bot.event
async def setup_hook():
  for filename in os.listdir(COGS_DIR):
    if filename.endswith('.py'):
        await bot.load_extension(f'cogs.{filename[:-3]}')
        print(f"Loaded Cog: {filename[:-3]}")
    else:
        print("Unable to load pycache folder.")

bot.run(API_TOKEN)
