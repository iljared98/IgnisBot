import discord
from discord.ext import commands
import os
from urllib import request
from urllib.request import Request, urlopen
import time
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs



class downloadStreamCommands(commands.Cog):

    """Commands involving downloading files, web scraping, and streaming video."""

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ytInfo(ctx, URL, *args):
        with youtube_dl.YoutubeDL() as ydl:
            meta = ydl.extract_info(URL, download=False)

        upload_date = meta.get('upload_date')
        post_date = f'{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}'
        duration = meta.get('duration')
        seconds = duration
        mins = seconds // 60
        if mins >= 60:
          seconds = duration % (24 * 3600) 
          hour = seconds // 3600
          seconds %= 3600
          minutes = seconds // 60
          seconds %= 60
          finalDur = "%d:%02d:%02d" % (hour, minutes, seconds)
        else:
          seconds = duration % (24 * 3600) 
          seconds %= 3600
          minutes = seconds // 60
          seconds %= 60
          finalDur = "%02d:%02d" % (minutes, seconds)
        if 'desc' in args:
          embed = discord.Embed(
            title = meta.get('title'),
            description = meta.get('description'),
            colour = discord.Colour.red()
          )
        else:
          embed = discord.Embed(
            title = meta.get('title'),
            colour = discord.Colour.dark_red()
          )

          embed.set_image(url = meta.get('thumbnail'))
          embed.add_field(name='Upload Date', value=post_date, inline=True)
          embed.add_field(name='Views', value=format(meta.get('view_count'), ',d'), inline=True)
          embed.add_field(name='Video Duration', value=finalDur, inline=True)
          embed.add_field(name='Likes', value=format(meta.get('like_count'), ',d'), inline=True)
          embed.add_field(name='Dislikes', value=format(meta.get('dislike_count'), ',d'), inline=True)
          embed.add_field(name='Author', value=meta.get('uploader'), inline=True)

          await ctx.send(embed = embed)



def setup(client):
  client.add_cog(downloadStreamCommands(client))
