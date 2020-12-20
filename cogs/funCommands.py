import discord
import os
import random
from random import randint
from discord.ext import commands
import re
import urllib.parse, urllib.request
import urbandictionary as ud
'''
VERY IMPORTANT NOTE FOR THE URBAN DICTIONARY MODULE
Do NOT use pip or PyPI to install this module, as that installation method is out of date.

1. Find your local Python install and all of its modules (usually in appdata and 
   the module folder is in .../libs/site-packages/
2. Go to the UrbanDictionary wrapper repository (https://github.com/bocong/urbandictionary-py),
   download the repo in a .zip file and save it in the folder containing your modules. Extract the repo folder.
3. Open command prompt/terminal, navigate to the folder containing the UrbanDictionary module itself (one level
   lower than the module directory).
4. Run "python setup.py install"
5. After this you should be able to import the latest version without any problems.
'''

class Recreational(commands.Cog):

    """Commands for user entertainment."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def russrul(self, ctx):
        chambers = [1, 2, 3, 4, 5, 6]
        bang = random.choice(chambers)
        pull = random.choice(chambers)
        if bang != pull:
            await ctx.send('*Click!* {} has survived!'.format(ctx.author.mention))
        elif bang == pull:
            await ctx.send('*BANG!* {} has died!'.format(ctx.author.mention))


    @commands.command()
    async def roll(self, ctx, rollmin: int, rollmax: int):
        rollVal = randint(rollmin, rollmax)
        await ctx.send(f'{ctx.author.mention} rolled: {rollVal}!')

    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        if len(question) == 0:
            await ctx.send(f':warning: {ctx.author.mention} Cannot predict off of a blank input.', delete_after=15)
        else:
            responseList = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes - definitely.',
                            'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                            'Signs point to yes.', 'Reply hazy, try again later.', 'Ask another time.',
                            "Don't ask questions you don't want to know the answer to.", 'Cannot predict now.',
                            'Ask your mother.', "Don't count on it.", 'My reply is no.', 'My sources say no.',
                            'Outlook not so good.', 'Very doubtful.']
            await ctx.send(f'{ctx.author.mention}  Question: {question}\nAnswer: {random.choice(responseList)}')

    @commands.command()
    async def hope(self, ctx):

        
        hope_path = os.path.abspath('assets/feels/hope.jpg') 
        await ctx.send(content=f"{ctx.author.mention} Have hope my fellow kings!", file=discord.File('{}'.format(hope_path)))

    @commands.command()
    async def pain(self, ctx):
        responses = ["**DON'T CALL IT A GRAVE, IT'S THE FUTURE YOU CHOSE**", "**THE BELLS TOLL FOR THEE**",
                     "**WHEN WILL YOU LEARN THAT YOUR ACTIONS HAVE CONSEQUENCES**", "**THE ABYSS HAS FINALLY STARED BACK**"]
        fileUpload = random.choice(os.listdir("assets/feels/pain/"))
        await ctx.send(content=f"{random.choice(responses)}", file=discord.File(f'assets/feels/pain/{fileUpload}'))

    @commands.command()
    async def lol(self, ctx):
        vid = random.choice(os.listdir("assets/lol/"))
        await ctx.send(content=f'', file=discord.File(f'assets/lol/{vid}'))

    @commands.command()
    async def kino(self, ctx, *,input): # FIXME: Add new logic to determine which link to post to the chat!

        if 'joker' in input.lower():
            await ctx.send('SOCIETY\nhttps://cdn.discordapp.com/attachments/699151253321547857/710905743808659486/joker_movie.webm')
        elif 'spongebob' in input.lower() or 'spangbab' in input.lower():
            krabsPiracy = ["Ahoy SpongeBob me boy, piracy is illegal in the United States of America! ARGH ARGH ARGH ARGH!",
                           "Ahoy SpongeBoy me Bob, I am going to get sued by Viacom for posting the full SpongeBob movie! ARGH ARGH ARGH ARGH!",
                           "Ahoy SpongeBob me boy, I found a shitty camera rip of the original SpongeBob movie! ARGH ARGH ARGH ARGH!"]
            krabsPiracyResponse = random.choice(krabsPiracy)
            await ctx.send(f"{krabsPiracyResponse}\n https://cdn.discordapp.com/attachments/581533299491733570/632748985022414878/spongebob_first_movie.mp4")
        elif 'shrek' in input.lower() or 'ogre' in input.lower():
            await ctx.send("DUNKEY, WHAT ARE YA DOIN' IN MY SWAMP?!\nhttps://cdn.discordapp.com/attachments/639999420779462669/640368704185565194/Shrek.mp4")
        elif 'bee' in input.lower():
            await ctx.send('KINO IS BACK ON THE MENU BOYS\nhttps://cdn.discordapp.com/attachments/419074439703953411/437179464619786261/beemovie.mp4')
        else:
            await ctx.send(':warning: Your search did not come up with any results, please try again!')


    @commands.command(aliases=['chokememe','chokes'])
    async def choke(self, ctx):
        chokeImg = random.choice(os.listdir("assets/choke/"))
        await ctx.send(content=f'', file=discord.File(f'assets/choke/{chokeImg}'))

    @commands.command(aliases=['feedandseed','chuck','fuckandsuck'])
    async def sneed(self, ctx):
        sneedImg = random.choice(os.listdir("assets/sneed/"))
        await ctx.send(content=f'', file=discord.File(f'assets/sneed/{sneedImg}'))

    @commands.command()
    async def ascii_movie(self, ctx, *args):
        joinArgs = ' '.join(args)
        if '|' not in args:
            joinArgs += '|'
            joinArgs += ''
        words = joinArgs.split('|')
        if len(words) > 2:
            await ctx.send(f':warning: {ctx.author.mention} Too many arguments given. Marquee can have a maximum of 2 lines.')
        else:
            if len(words[0]) > 29 or len(words[1]) > 29:
                await ctx.send(f':warning: {ctx.author.mention} The marquee title/subtitle can be a maximum of 29 characters.', delete_after=15)
            else:
                x = 29 - len(words[0].strip())
                y = 29 - len(words[1].strip())
                spaceX = ' ' * int(x / 2)
                spaceY = ' ' * int(y / 2)
                finMessageX = f'{spaceX}{words[0].upper().strip()}{spaceX}'
                finMessageY = f'{spaceY}{words[1].upper().strip()}{spaceY}'
                if len(finMessageX) != 30:
                    while len(finMessageX) != 30:
                        finMessageX += ' '
                if len(finMessageY) != 30:
                    while len(finMessageY) != 30:
                        finMessageY += ' '
                await ctx.send(f"""```
                          @-_________________-@
                    @-_____|   NOW SHOWING   |______-@
                     |{finMessageX}|
                     |{finMessageY}|
             ________|______________________________|_________
            |________________________________________________|
            |               -                -               |
            |   -       -             -                    - |
            |        ____    ______________-   ____          |
            | -  -  |    |   |  TICKETS   |   |    | -       |
            |       |    |   |            |   |    |         |
            |  --   |____| - |_o___oo___o_| - |____|     -   |
            | -     |    |  |     --       |  |    |         |
            |    -  |    |- | -      -     |  |    | --      |
            |_______|====|__|______________|__|====|_________|
           /                                                  \\
         
        ```""")

    @commands.command(aliases=['urbandict','urbandictionary','urb'])
    async def urban(self, ctx, *args):

        query = str(' '.join(args))
        defs = ud.define(f'{query}')
        if len(defs) >= 1:
            for i in defs:
                embed = discord.Embed(title=f'__**{i.word}**__',description=f'__Definition:__\n{i.definition}\n\n__Example:__\n*{i.example}*')
                await ctx.send(embed=embed)
                break
        else:
            query = str(' '.join(args))
            await ctx.send(f":warning: {ctx.author.mention} Couldn't find word term : {query}")

    @commands.command(aliases=['asskey_comp','ascii_comp','computer'])
    async def ascii_computer(self, ctx, *args):
        pass

    @commands.command(aliases=['yt'])
    async def youtube(self, ctx, *, query):
        try:
            search = urllib.parse.urlencode({
                'search_query' : query
            })
            content = urllib.request.urlopen('https://www.youtube.com/results?' + search)
            results = re.findall(r'/watch\?v=(.{11})', content.read().decode()) #FIXME: Keep an eye on this, a Youtube update
                                                                                # nearly broke this aspect of the command last time.
            await ctx.send('https://youtube.com/watch?v=' + results[0])

        except:
            await ctx.send(f':warning: {ctx.author.mention} **Video could not be found/processed.**')

    @commands.command(aliases=['gameinfo'])
    async def igdb(self, ctx, *, query):
        pass

    @commands.command(name='soy', aliases=['soi']) #FIXME: Add the text from the post above the command and greentext it.
    async def soyCommand(self, ctx):
        postImg = random.choice(os.listdir("assets/soy/"))
        await ctx.send(content=f'PLACEHOLDER', file=discord.File(f'assets/soy/{postImg}'))


def setup(bot):
  bot.add_cog(Recreational(bot))
