import discord
from discord.ext import commands
import datetime
from datetime import datetime, timedelta
import platform
from wikipedia import wikipedia as wk
import wolframalpha as wa
from pyowm import OWM
import os
import nasapy
import toml
import asyncio 
import re
import aiohttp
from pathlib import Path

config = toml.load("config.toml")

WA_KEY = config["WOLFRAM_ALPHA"]
NASA_KEY = config["NASA"]
OWM_KEY = config["OPEN_WEATHER_MAP"]

# TODO: Make these pull from a TOML config instead.
POTD_CACHE_DIR = Path("assets/potd_cache")
POTD_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class Utility(commands.Cog):

  """General purpose commands."""

  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ping(self, ctx):
    
    embed = discord.Embed(
      title="IgnisBot - Ping",
      description=f'Ping: {int(self.bot.latency * 1000)}ms'
    )

    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

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

  # TODO: Rewrite and document this command. 
  @commands.command()
  async def help(self, ctx, *cog):
    if not cog:
      embed = discord.Embed(description="__IgnisBot Help__")
      cog_desc = ""
      for item in self.bot.cogs:
        cog_desc += f'**{item}** - *{self.bot.cogs[item].__doc__}*\n'
      embed.add_field(name='**Cogs**', value=cog_desc)
      await ctx.send(embed=embed)

  @commands.command(aliases=['wikipedia', 'wk'])
  async def wiki(self, ctx, *args):
    argString = str(' '.join(args))
    page = None
    
    try:
        page = wk.page(argString, auto_suggest=False)
        if not page.title or not page.url:
            raise Exception("Invalid page response")

    except:
        search_results = wk.search(argString)
        if search_results:
            page = wk.page(search_results[0])
        else:
            await ctx.send(f':warning: {ctx.author.mention} No matching Wikipedia page found for: {argString}')
            return
    
    if page and hasattr(page, 'title') and hasattr(page, 'url'):
        try:
            page = wk.page(page.title, auto_suggest=False)
        except wk.DisambiguationError as e:
            page = wk.page(e.options[0], auto_suggest=False) 
    
    images = getattr(page, 'images', [])
    selected_image = None

    WIKI_IMG_KEYWORDS = config["WIKI_IMG_KEYWORDS"] # We look for the first possible image that matches a keyword / phrase before preferring page title matches 
                                                    # (or first image found)
    if images:
        for img in images:
            lower_img = img.lower()
            #
            if any(keyword in lower_img for keyword in WIKI_IMG_KEYWORDS):
                print('found match on keyword')
                selected_image = img
                break

            if not selected_image:
                title_parts = [re.sub(r'[^a-zA-Z0-9]', '', part).lower() for part in page.title.split()]
                for img in images:
                    if any(part in img.lower() for part in title_parts):
                        print('found match on split title')
                        selected_image = img
                        break

            if not selected_image:
                print('picking first picture')
                selected_image = images[0]
    
    embed = discord.Embed(title=page.title, description=wk.summary(page.title, sentences=3, auto_suggest=False))
    if selected_image:
        embed.set_image(url=selected_image)
    embed.add_field(name='*To read more, click the link below:*', value=f'*{page.url}*')
    
    await ctx.send(embed=embed)

  #! Fix this, command is broken. 
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

  #! Fix, error outputs Client.aquery was never awaited. 
  @commands.command(aliases=['wolfram', 'wa', 'wolf'])
  async def wolframalpha(self, ctx, *, query):
      try:
          wolfram_client = wa.Client(WA_KEY)
          embed = discord.Embed(description=f'**__Question:__** *{query}*')

          def sync_query(client, query):
              return client.query(query)

          # Run the synchronous WolframAlpha query in a separate thread
          search = await asyncio.to_thread(sync_query, wolfram_client, query)
          result = next(search.results).text
          embed.add_field(name='Answer', value=f'{result}')

          embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/644436203315396629/305ad4cf60fd9bc0f787e6c95c5523d3.png')
          # embed.set_image(url=resImg)
          await ctx.send(embed=embed)
      except Exception as e:
          await ctx.send(f':warning: {ctx.author.mention} Wolfram|Alpha was not able to process your query. Please try again. {e}')


  #! Broken, need to update this. 
  @commands.command(name='potd')
  async def potdCommand(self, ctx):
      date = datetime.today().date()
      message = await self.send_apod_embed(ctx, date)

      # Add initial reactions
      await message.add_reaction("⬅️")
      if date < datetime.today().date():
          await message.add_reaction("➡️")
      await message.add_reaction("❌")

      def check(reaction, user):
          return (
              user == ctx.author
              and str(reaction.emoji) in ["⬅️", "➡️", "❌"]
              and reaction.message.id == message.id
          )

      while True:
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "⬅️":
                date -= timedelta(days=1)

            elif str(reaction.emoji) == "➡️":
                if date < datetime.today().date():
                    date += timedelta(days=1)

            elif str(reaction.emoji) == "❌":
                try:
                    await message.clear_reactions()
                except discord.Forbidden:
                    for emoji in ["⬅️", "➡️", "❌"]:
                        await message.remove_reaction(emoji, self.bot.user)
                break

            # Delete the previous message
            await message.delete()

            # Send a new one with updated date
            message = await self.send_apod_embed(ctx, date)

            # Re-add valid navigation reactions
            await message.add_reaction("⬅️")
            if date < datetime.today().date():
                await message.add_reaction("➡️")
            await message.add_reaction("❌")

        except asyncio.TimeoutError:
            try:
                await message.clear_reactions()
            except:
                pass
            break

  async def download_image(self, session, url, filename):
    async with session.get(url) as resp:
        if resp.status == 200:
            with open(filename, 'wb') as f:
                f.write(await resp.read())
            return filename
        return None

  async def send_apod_embed(self, ctx, date):
      nasa = nasapy.Nasa(key=NASA_KEY)
      apod = nasa.picture_of_the_day(date=date.strftime('%Y-%m-%d'), hd=True)

      explanation = apod.get("explanation", "")
      if len(explanation) > 4096:
          explanation = explanation[:4093] + "..."

      embed = discord.Embed(
          title=apod.get("title", "NASA Picture of the Day"),
          description=explanation,
          color=discord.Color.green()
      )

      media_type = apod.get("media_type", "")
      url = apod.get("url", "")
      image_url = url

      file = None
      if media_type == "image" and image_url:
          filename = POTD_CACHE_DIR / f"potd_{date.strftime('%Y%m%d')}.jpg"
          async with aiohttp.ClientSession() as session:
              downloaded = await self.download_image(session, image_url, filename)
              if downloaded:
                  file = discord.File(fp=filename, filename=filename.name)
                  embed.set_image(url=f"attachment://{filename.name}")
                  embed.set_thumbnail(url=ctx.author.display_avatar.url)
              else:
                  embed.add_field(name="Image Unavailable", value=image_url, inline=False)

      elif media_type == "video":
          embed.add_field(name="Video Preview", value=url, inline=False)
          embed.set_thumbnail(url=ctx.author.display_avatar.url)
      else:
          embed.add_field(name="Media", value=url or "No media found.", inline=False)

      embed.set_footer(text=f'NASA Picture of the Day : {date.strftime("%m-%d-%Y")}')

      if file:
          return await ctx.send(embed=embed, file=file)
      return await ctx.send(embed=embed)



  @commands.command(name='weather')
  async def weatherCommand(self, ctx, *, query):
    """ Pulls a detailed one day forecast from a zip code / city name, from the OpenWeatherMap API."""
    try:
        owm = OWM(OWM_KEY)
        mgr = owm.weather_manager()

        # Zip code / name search. 
        if query.isdigit() and len(query) == 5:
            location = f"{query}, US"  
        else:
            location = query

        observation = mgr.weather_at_place(location)
        w = observation.weather

        temperature = w.temperature('fahrenheit')
        wind = w.wind(unit='miles_hour')
        description = w.detailed_status.capitalize()
        icon_code = w.weather_icon_name
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

        embed = discord.Embed(
            title=f"Weather for {location.title()}",
            description=description,
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=icon_url)
        embed.add_field(name='Temp (Low)', value=f'{temperature["temp_min"]} °F')
        embed.add_field(name='Temp (High)', value=f'{temperature["temp_max"]} °F')
        embed.add_field(name='Humidity', value=f'{w.humidity}%')
        embed.add_field(name='Wind Speed', value=f'{round(float(wind["speed"]), 2)} mph')

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"[Weather Error] {e}")  # Debug log
        await ctx.send(f':warning: {ctx.author.mention} There was an issue with your OpenWeatherMap query. Please check the city name or ZIP code and try again.')


  @commands.command(name='weatherweek', aliases=['fivedayforecast'])
  async def fiveDayForecast(self, ctx, *, query):
      """ Pulls a five day forecast from a zip code / city name, from the OpenWeatherMap API."""
      try:
          owm = OWM(OWM_KEY)
          mgr = owm.weather_manager()

          # Zip code / name search
          if query.isdigit() and len(query) == 5:
              location = f"{query}, US"
          else:
              location = query

          observation = mgr.weather_at_place(location)
          w = observation.weather

          # Get the 5-day forecast (every 3 hours)
          forecast = mgr.forecast_at_place(location, '3h')

          embed = discord.Embed(
              title=f"Weather for {location.title()}",
              color=discord.Color.blue()
          )

          # Keep track of the days added to avoid duplicates
          added_dates = set()

          # Loop through forecast data, but only add one entry per day
          for forecast_data in forecast.forecast:
              date = datetime.utcfromtimestamp(forecast_data.reference_time())
              date_str = date.strftime('%Y-%m-%d')

              # Skip if we've already added a forecast for this date
              if date_str in added_dates:
                  continue

              # Add this date to the set to avoid adding it again
              added_dates.add(date_str)

              temperature = forecast_data.temperature('fahrenheit')
              wind = forecast_data.wind(unit='miles_hour')
              description = forecast_data.detailed_status.capitalize()
              icon_code = forecast_data.weather_icon_name
              icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

              embed.add_field(
                  name=f"Forecast for {date_str}",
                  value=(
                      f"**Description:** {description}\n"
                      f"**Temp:** {temperature['temp']} °F\n"
                      f"**Humidity:** {forecast_data.humidity}%\n"
                      f"**Wind Speed:** {round(float(wind['speed']), 2)} mph"
                  ),
                  inline=False
              )

          embed.set_thumbnail(url=icon_url)
          await ctx.send(embed=embed)

      except Exception as e:
          print(f"[Weather Error] {e}")  # Debug log
          await ctx.send(f':warning: {ctx.author.mention} There was an issue with your OpenWeatherMap query. Please check the city name or ZIP code and try again.')



async def setup(bot):
  await bot.add_cog(Utility(bot))
