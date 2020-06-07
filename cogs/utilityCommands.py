import discord
from discord.ext import commands
from datetime import datetime
import platform
from wikipedia import wikipedia as wk
import pyshorteners
#import google
import wolframalpha as wa

import bs4
import os
from configparser import ConfigParser as cp

config = cp()
cfgpath = os.getcwd() + "//ignis.cfg"
config.read(cfgpath)
WA_KEY = config.get("API_KEYS", "wolfkey")

class Utility(commands.Cog):

  """General purpose commands."""

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f'Ping: {int(self.bot.latency * 1000)}ms')

  @commands.command()
  async def dt(self, ctx):
    now = datetime.now()
    dt_str = now.strftime("%m/%d/%Y %H:%M:%S")
    await ctx.send(f'Current Time and Date : {dt_str}')

  @commands.command() # Number of guilds joined, users in current guild, python version, maybe add more?
  async def stats(self, ctx):
    pyVersion = platform.python_version()
    serversJoined = len(self.bot.guilds)
    userCount = len(set(self.bot.get_all_members()))
    statEmbed = discord.Embed(title="IgnisBot Statistics",description=f":snake: **Python Version:** {pyVersion}\n\n:computer: **Server Count:** {serversJoined}\n\n:family: **Users Count:** {userCount}")

    await ctx.send(embed=statEmbed)

  # Needs to be expanded upon, have an embed generated for each command name/description later on.
  @commands.command()
  async def help(self, ctx, *cog):
    if not cog:
      embed = discord.Embed(description="__IgnisBot Help__")
      cog_desc = ""
      for item in self.bot.cogs:
        cog_desc += f'**{item}** - *{self.bot.cogs[item].__doc__}*\n'
      embed.add_field(name='**Cogs**', value=cog_desc)
      await ctx.send(embed=embed)


  # FIXME: Returns the correct article for the most part, but it requires
  #        user queries to be VERY specific. Currently leaving this as is, because
  #        the core functionality works in 90% of cases. If you can figure out how to
  #        make it require a less specific input, let me know.

  @commands.command(aliases=['wikipedia', 'wikisearch', 'wik', 'wikiquery','wk'])
  async def wiki(self, ctx, *args):
    try:
      argString = str(' '.join(args))
      s = pyshorteners.Shortener()
      embed = discord.Embed(title=f'{wk.page(argString).title}', description=f'{wk.summary(argString, sentences=3)}')
      embed.set_image(url=f'{wk.page(argString).images[0]}')
      embed.add_field(name=f'*To read more, click the link below:*', value=f'*{s.chilpit.short(wk.page(argString).url)}*')
      await ctx.send(embed=embed)

    except:
      argString = str(' '.join(args))
      await ctx.send(f':warning: {ctx.author.mention} Could not process/find page : {argString}')

  @commands.command(aliases=['userinfo','whois'])
  async def info(self, ctx, *, member: discord.Member):
    embed = discord.Embed()

    embed.set_author(name=f'Account Information : {member}')
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name='ID:', value=f'{member.id}')
    embed.add_field(name='Display Name:', value=f'{member.display_name}')
    embed.add_field(name='Creation Date:',value=f'{member.created_at.strftime(f"%m/%d/%Y %I:%M UTC")}')
    embed.add_field(name='Join Date:', value=f'{member.joined_at.strftime(f"%m/%d/%Y %I:%M UTC")}')

    await ctx.send(embed=embed)

  '''
  @commands.command(aliases=['goggle','goog','goo.gl'])
  async def google(self, ctx, *, query):
    pass
  '''

  # FIXME: Eventually will require the command to display images and graphs for the user should they desire them
  #        However in the meantime, the user is still able to have 90% of queries answered, so we'll leave it as is.

  @commands.command(aliases=['wolfram','wa','wolf'])
  async def wolframalpha(self, ctx, *, query):
    try:
      client = wa.Client(WA_KEY)
      embed = discord.Embed(description=f'**__Question:__** *{query}*')

      search = client.query(query)
      result = next(search.results).text
      #resImg = result['queryresult']['pods'][0]['subpods'][0]['imagesource']
      embed.add_field(name='Answer',value=f'{result}')

      embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/644436203315396629/305ad4cf60fd9bc0f787e6c95c5523d3.png')
      #embed.set_image(url=resImg)
      await ctx.send(embed=embed)
    except:
      await ctx.send(f':warning: {ctx.author.mention} Wolfram|Alpha was not able to process your query. Please try again.')

  @commands.command()
  async def poll(self, ctx):
    pass

 # @commands.command()


def setup(bot):
  bot.add_cog(Utility(bot))
