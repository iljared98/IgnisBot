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

    # FIXME : Add global command cooldown of 30 seconds so multiple requests for the command
    #       don't fuck it up! Or find a more elegant implementation for this process, whatever works!
    #       Also, find a way to get the .zip file to the user.

    # Use this to host files, maybe find a way to grab the .zip off of the page after uploading.
    # https://volafile.org/r/19yk6apuc
    '''
    @commands.command(aliases=['chan','chandownload','chanarchive'])
    async def chanscrape(self, ctx, *, input):
        try:
            chanpath = 'h'
            if '4chan' or '4channel' in input:
                await ctx.send(f'{ctx.mention.author} Downloading requested thread, please wait until the process is complete!')
            elif '8kun.top' in input:
                await ctx.send(f'{ctx.mention.author} Downloading requested thread, please wait until the process is complete!')
            elif '9chan' in input:
                await ctx.send(f'{ctx.mention.author} Downloading requested thread, please wait until the process is complete!')
            else:
                await ctx.send(f':warning: {ctx.mention.author}, the thread URL you gave is not valid. Please enter a valid thread URL and try again!')
        except:
            await ctx.send(f':warning: An error has occurred, please check your input and try again!')
    '''




def setup(client):
  client.add_cog(downloadStreamCommands(client))