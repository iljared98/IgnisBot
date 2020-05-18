import discord
from discord.ext import commands
from datetime import datetime
import platform

class utilCommands(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    now_ready = datetime.now()
    dt_str_ready = now_ready.strftime("%m/%d/%Y %H:%M:%S")
    print("Ignis Bot ::::: ONLINE\n\n{}".format(dt_str_ready))
    await self.client.change_presence(activity=discord.Game(name='Valorant sucks'))

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f'Ping: {int(self.client.latency * 1000)}ms')

  @commands.command()
  async def dt(self, ctx):
    now = datetime.now()
    dt_str = now.strftime("%m/%d/%Y %H:%M:%S")
    await ctx.send(f'Date-Time: {dt_str}')

  @commands.command() # Number of guilds joined, users in current guild, python version,
  async def stats(self, ctx):
    pyVersion = platform.python_version()
    serversJoined = len(self.client.guilds)
    userCount = len(set(self.client.get_all_members()))
    statEmbed = discord.Embed(title="IgnisBot Statistics",description=f"**Python Version:** {pyVersion}\n**Server Count:** {serversJoined}\n**Users Count:** {userCount}")

    await ctx.send(embed=statEmbed)





def setup(client):
  client.add_cog(utilCommands(client))
