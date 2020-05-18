# :^)

import discord
import datetime
from datetime import datetime
import os
import logging
from os import path
from configparser import ConfigParser as cp # Used to grab the token and command prefix
from discord.ext import commands


config = cp()
cfgpath = os.getcwd() + "//ignis.cfg"
config.read(cfgpath)

# Gets the token and command prefix for you, requires a .cfg to do this.
token = config.get("DEFAULT", "token")
prefix = config.get("DEFAULT", "prefix")

client = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id='138452291085664256')

# FIXME: Add try/except blocks to avoid problems with the commands

@client.command()
async def load(ctx, extension):
  client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')





client.run(token)