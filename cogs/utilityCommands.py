import discord
from discord.ext import commands
from datetime import datetime
import platform
import wikipedia

class utilCommands(commands.Cog):

  """General purpose commands."""

  def __init__(self, client):
    self.client = client

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f'Ping: {int(self.client.latency * 1000)}ms')

  @commands.command()
  async def dt(self, ctx):
    now = datetime.now()
    dt_str = now.strftime("%m/%d/%Y %H:%M:%S")
    await ctx.send(f'Current Time and Date : {dt_str}')

  @commands.command() # Number of guilds joined, users in current guild, python version, maybe add more?
  async def stats(self, ctx):
    pyVersion = platform.python_version()
    serversJoined = len(self.client.guilds)
    userCount = len(set(self.client.get_all_members()))
    statEmbed = discord.Embed(title="IgnisBot Statistics",description=f":snake: **Python Version:** {pyVersion}\n\n:computer: **Server Count:** {serversJoined}\n\n:family: **Users Count:** {userCount}")

    await ctx.send(embed=statEmbed)

  # Needs to be expanded upon, have an embed generated for each command name/description later on.
  @commands.command()
  async def help(self, ctx, *cog):
    if not cog:
      embed = discord.Embed(description="__IgnisBot Help__")
      cog_desc = ""
      for item in self.client.cogs:
        cog_desc += f'**{item}** - *{self.client.cogs[item].__doc__}*\n'
      embed.add_field(name='**Cogs**', value=cog_desc)
      await ctx.send(embed=embed)


  # FIXME: Things that work: properly returns article summary
  #        Things that need to be fixed: returning the article picture (or IgnisBot's avatar, if
  #                                      the article doesn't have one), returning the correct title
  #        Quality of life: find a more elegant way to cut off the end of the article, make it look
  #                         less shitty, like ending it with whitespace

  @commands.command(aliases=['wikipedia', 'wikisearch', 'wik', 'wikiquery'])
  async def wiki(self, ctx, *, query):

    realQuery = wikipedia.search(query)
    #try:
    wk = wikipedia.page(auto_suggest=False, redirect=True)
    queryResult = wikipedia.summary(query)
    summaryLen = len(queryResult)
    if summaryLen >= 2048:
      while summaryLen != 1000:
        queryResult = queryResult[:-1]
        summaryLen = summaryLen - 1
      queryResult = queryResult + ' [...]'
      wikiEmbed = discord.Embed(title=f'__**{wk.title}**__', image=wk.images[0], description=f'{queryResult}')
      await ctx.send(embed=wikiEmbed)

    else:
      wikiEmbed = discord.Embed(title=f'__**{wk.title}**__'.upper(), image=wk.images[0], description=f'{queryResult}')
      await ctx.send(embed=wikiEmbed)
      
def setup(client):
  client.add_cog(utilCommands(client))
