import discord
from discord.ext import commands
import datetime
from datetime import datetime
import platform
#import pandas as pd
#from iexfinance.stocks import get_historical_data
#from iexfinance.stocks import get_historical_intraday
from iexfinance.stocks import Stock
from wikipedia import wikipedia as wk
import pyshorteners
#import google
import wolframalpha as wa
from pyowm import OWM
#import bs4
import os
import nasapy
#import json
from configparser import ConfigParser as cp

config = cp()
cfgpath = os.getcwd() + "//ignis.cfg"
config.read(cfgpath)

WA_KEY = config.get("API_KEYS", "wolfkey")
STOCK_KEY = config.get("API_KEYS", "iexcloudPUBLISH")
STOCK_KEY_PRIV = config.get("API_KEYS", "iexcloudSECRET")
NASA_KEY = config.get("API_KEYS", "nasa")
OWM_KEY = config.get("API_KEYS", "openweathermap")


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

  @commands.command() # FIXME: Number of guilds joined, users in current guild, python version, maybe add more?
  async def stats(self, ctx):
    pyVersion = platform.python_version()
    serversJoined = len(self.bot.guilds)
    userCount = len(set(self.bot.get_all_members()))
    statEmbed = discord.Embed(title="IgnisBot Statistics",
                              description=f":snake: **Python Version:** {pyVersion}"
                                          f"\n\n:computer: **Server Count:** {serversJoined}"
                                          f"\n\n:family: **Users Count:** {userCount}")

    await ctx.send(embed=statEmbed)

  @commands.command()
  async def help(self, ctx, *cog):
    if not cog:
      embed = discord.Embed(description="__IgnisBot Help__")
      cog_desc = ""
      for item in self.bot.cogs:
        cog_desc += f'**{item}** - *{self.bot.cogs[item].__doc__}*\n'
      embed.add_field(name='**Cogs**', value=cog_desc)
      await ctx.send(embed=embed)

  #FIXME: Rewrite this entire command or find a module that does its job better.
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

  @commands.command(aliases=['wolfram','wa','wolf'])
  async def wolframalpha(self, ctx, *, query): #FIXME: Add support for answers to return images; such as graphs, diagrams etc...
    try:
      client = wa.Client(WA_KEY)
      embed = discord.Embed(description=f'**__Question:__** *{query}*')

      search = client.query(query)
      result = next(search.results).text
      embed.add_field(name='Answer',value=f'{result}')

      embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/644436203315396629/305ad4cf60fd9bc0f787e6c95c5523d3.png')
      #embed.set_image(url=resImg)
      await ctx.send(embed=embed)
    except:
      await ctx.send(f':warning: {ctx.author.mention} Wolfram|Alpha was not able to process your query. Please try again.')

  @commands.command(name='stock', aliases=['stocks'])
  async def stockCommand(self, ctx, ticker):
    start = datetime.now() #FIXME: Potentially use another API instead, none of the desired fields will return despite
                           # being used according to the directions of their documentation. Troubleshoot this ASAP

    stock = Stock(str(ticker), token=STOCK_KEY)

    #df = get_historical_intraday(ticker, output_format='pandas', token=STOCK_KEY)
    #df = df.reindex(index=df.index[::-1])
    embed = discord.Embed()
    embed.set_author(name=stock.get_company_name())
    embed.add_field(name="Stock Price", value=f'${stock.get_price()}')
    #embed.add_field(name="Sector", value=stock.get_sector())
    #embed.add_field(name="Year High", value=f'${stock.get_years_high()}')
    #embed.add_field(name="Year Low", value=f"${stock.get_years_low()}")

    await ctx.send(embed=embed)

  @commands.command(name='potd')
  async def potdCommand(self, ctx):
    nasa = nasapy.Nasa(key=NASA_KEY)
    d = datetime.today().strftime('%Y-%m-%d')
    apod = nasa.picture_of_the_day(date=d, hd=True)
    try:

      embed = discord.Embed(title=f'{apod["title"]}',
                            description=f'{apod["explanation"]}')
      embed.set_image(url=f'{apod["hdurl"]}')
      embed.set_footer(text=f'NASA Picture of the Day : {datetime.today().strftime("%m-%d-%Y")}')
      await ctx.send(embed=embed)
    except: #FIXME: In case the description exceeds Discord's limits, it will simply send the embed without it. Be sure to clean up
            # this error checking in case it causes other problems.
      embed = discord.Embed(title=f'{apod["title"]}')
      embed.set_image(url=f'{apod["hdurl"]}')
      embed.set_footer(text=f'NASA Picture of the Day : {datetime.today().strftime("%m-%d-%Y")}')
      await ctx.send(embed=embed)


  @commands.command(name='weather') # FIXME: Add more specific functionality later, for now just enable city searching.
  async def weatherCommand(self, ctx, query):
    try:
      owm = OWM(OWM_KEY)
      mgr = owm.weather_manager()

      observation = mgr.weather_at_place(query)
      w = observation.weather

      embed = discord.Embed(title=f'{query.capitalize()}')
      embed.add_field(name='Temp Low', value=f'{w.temperature("fahrenheit")["temp_min"]} °F')
      embed.add_field(name='Temp High', value=f'{w.temperature("fahrenheit")["temp_max"]} °F')
      embed.add_field(name='Humidity', value=f'{w.humidity}%')
      embed.add_field(name='Wind Speed', value=f'{round(float(w.wind(unit="miles_hour")["speed"]), 2)} mph')

      await ctx.send(embed=embed)
    except:
      await ctx.send(f':warning: {ctx.author.mention} There was an issue with your Openweathermap query. Please try again.')

def setup(bot):
  bot.add_cog(Utility(bot))
