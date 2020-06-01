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

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id='138452291085664256')
bot.remove_command('help')

# FIXME: Add try/except blocks to avoid problems with the commands

@bot.event
async def on_ready():
  now_ready = datetime.now()
  dt_str_ready = now_ready.strftime("%m/%d/%Y %H:%M:%S")
  print("Ignis Bot ::::: ONLINE\n\n{}".format(dt_str_ready))
  await bot.change_presence(activity=discord.Game(name='Valorant sucks'))


# Loading all cog files;
for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    bot.load_extension(f'cogs.{filename[:-3]}')

'''
@bot.command()
async def load(ctx, extension):
  bot.load_extension(f'cogs.{extension}')
  
@bot.command()
async def unload(ctx, extension):
  bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
      bot.load_extension(f'cogs.{filename[:-3]}')
'''

bot.run(token)
