# Author      : Isaiah Jared
# Description : General purpose Discord bot. Used for
#               recreational and administrative
#               commands. Also features Youtube + local
#               audio playlist playback.



# ATTENTION #
# In place of using the .format() as seen in my other programs, try to use f-strings (f'insert text here')
# whenever possible. It allows for easier string formatting and soon enough the previous string formatting 
# methods will likely be phased out from future Python versions.


import random
from random import randint
import os
import discord
from discord.ext import commands
from datetime import datetime
from discord.utils import get
import youtube_dl
import asyncio

client = commands.Bot(command_prefix='-')
players = {}

@client.event
async def on_ready():
  now_ready = datetime.now()
  dt_str_ready = now_ready.strftime("%m/%d/%Y %H:%M:%S")
  print("Ignis Bot ::::: ONLINE\n\n{}".format(dt_str_ready))

  '''--------------- SERVER EVENTS --------------- '''
'''   --------------- --------------- --------------- '''

# FIXME: Join message events
'''
@client.event
async def on_join(member,channel):
  await channel.send(f'{member} has joined the server!')

@client.event
async def on_exit(member,channel):
  await channel.send(f'{member} has left the server!')
'''
'''--------------- ADMINISTRATIVE COMMANDS --------------- '''
'''   --------------- --------------- --------------- '''

@client.command()
async def ping(ctx):
  await ctx.send(f'Ping: {round(client.latency * 1000)}ms')

@client.command(aliases=['DT','Dt','dT'])
async def dt(ctx):
  now = datetime.now()
  dt_str = now.strftime("%m/%d/%Y %H:%M:%S")
  await ctx.send(f'Date-Time: {dt_str}')

@client.command(aliases=['ClearChat','Clearchat'])
async def clearchat(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

@client.command(aliases=['Kick','KICK'])
async def kick(ctx, member : discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f'Member {member.mention} has been kicked!')

@client.command(aliases=['Ban','BAN'])
async def ban(ctx, member : discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await ctx.send(f'Member {member.mention} has been banned!')

@client.command(aliases=['Unban','UNBAN'])
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split("#")

  for ban_entry in banned_users:
    user = ban_entry.user
    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'Member {member.mention} has been unbanned!')
      return


'''--------------- RECREATIONAL COMMANDS --------------- '''
'''   --------------- --------------- --------------- '''

# FIXME: Expand functionality with betting and passing the gun to other users
@client.command()
async def russrul(ctx):
    chambers = [1,2,3,4,5,6]
    bang = random.choice(chambers)
    pull = random.choice(chambers)
    if bang != pull:
        await ctx.send('*Click!* {} has survived!'.format(ctx.author.mention))
    elif bang == pull:
        await ctx.send('*BANG!* {} has died!'.format(ctx.author.mention))




@client.command()
async def roll(ctx, rollmax: int):
  rollVal = randint(1,rollmax)
  await ctx.send(f'You rolled: {rollVal}!')

@client.command(aliases=['8ball','8Ball'])
async def _8ball(ctx, *, question):
  responseList = ['It is certain.','It is decidedly so.','Without a doubt.','Yes - definitely.','You may rely on it.','As I see it, yes.','Most likely.','Outlook good.','Yes.','Signs point to yes.','Reply hazy, try again later.','Ask another time.',"Don't ask questions you don't want to know the answer to.",'Cannot predict now.','Ask your mother.',"Don't count on it.",'My reply is no.','My sources say no.','Outlook not so good.','Very doubtful.']

  await ctx.send(f'Question: {question}\nAnswer: {random.choice(responseList)}')

'''--------------- WEB COMMANDS --------------- '''
'''   --------------- --------------- --------------- '''

# https://github.com/appu1232/Discord-Selfbot/wiki/Google-API-Setup-for-Image-Search-Command
# https://developers.google.com/custom-search/v1/overview?refresh=1
'''
@client.command(aliases=['Google'])
async def google()

@client.command(aliases=['yt','Yt','yT','Youtube','YouTube'])
await def youtube()
  pass

@client.command(aliases=['Img','IMG'])
await def img()
  pass

@client.command()
'''

'''--------------- IMAGE/VIDEO COMMANDS --------------- '''
'''   --------------- --------------- --------------- '''


@client.command(aliases=['Hope'])
async def hope(ctx):
  hope_path = os.path.abspath('assets/feels/hope.jpg')
  await ctx.send(content="Have hope my fellow kings!",file=discord.File('{}'.format(hope_path)))

@client.command(aliases=['Pain'])
async def pain(ctx):
  pain_path = os.path.abspath('assets/feels/pain.jpg')
  await ctx.send(content="DON'T CALL IT A GRAVE, IT'S THE FUTURE YOU CHOSE",file=discord.File('{}'.format(pain_path)))


@client.command(aliases=['LOL','Lol','LoL'])
async def lol(ctx):
  lolPath = os.path.abspath('assets/lol/')
  lolExt = (".mp4", ".webm")
  lolList = []
  for file in os.listdir(lolPath):
    if file.endswith(lolExt):
      lolList.append(os.path.join(lolPath,file))

  lolChosen = random.choice(lolList)
  await ctx.send(file=discord.File('{}'.format(lolChosen)))

@client.command()
async def spangbab(ctx):
  krabsPiracy = ["Ahoy SpongeBob me boy, piracy is illegal in the United States of America! ARGH ARGH ARGH ARGH!", "Ahoy SpongeBoy me Bob, I am going to get sued by Viacom for posting the full SpongeBob movie! ARGH ARGH ARGH ARGH!","Ahoy SpongeBob me boy, I found a shitty camera rip of the original SpongeBob movie! ARGH ARGH ARGH ARGH!"]
  krabsPiracyResponse = random.choice(krabsPiracy)
  await ctx.send(f"{krabsPiracyResponse}\n https://cdn.discordapp.com/attachments/581533299491733570/632748985022414878/spongebob_first_movie.mp4")

'''--------------- VOICE CHANNEL COMMANDS --------------- '''
'''   --------------- --------------- --------------- '''

'''
@client.command(aliases=['Join','JOIN'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    await voice.disconnect()
    await ctx.send(f'Joined {channel}!')

@client.command(aliases=['Leave', 'LEAVE'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"IgnisBot: Left {channel}.")
    else:
        await ctx.send("IgnisBot: Not currently in voice channel.")

@client.command(aliases=['Play','PLAY'])
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
'''



# Insert token here
client.run('TOKEN')
