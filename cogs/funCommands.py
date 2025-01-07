import discord
import os
import random
from random import randint
from discord.ext import commands
import re
import urllib.parse, urllib.request
from modules.urbandictionary import get_best_definition


class Recreational(commands.Cog):

    """Commands for user entertainment."""

    def __init__(self, bot):
        self.bot = bot


    #! Use this to demo SQLite3, add a points system. 
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

    #! Prettify this (and roll command), maybe toss them in embeds?
    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        if len(question) == 0:
            await ctx.send(f':warning: {ctx.author.mention} Cannot predict off of a blank input.', delete_after=15)
        else:

            # TODO: Populate this with a list of preset strings in config.toml
            responseList = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes - definitely.',
                            'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                            'Signs point to yes.', 'Reply hazy, try again later.', 'Ask another time.',
                            "Don't ask questions you don't want to know the answer to.", 'Cannot predict now.',
                            'Ask your mother.', "Don't count on it.", 'My reply is no.', 'My sources say no.',
                            'Outlook not so good.', 'Very doubtful.']
            await ctx.send(f'{ctx.author.mention}  Question: {question}\nAnswer: {random.choice(responseList)}')

    @commands.command()
    async def hope(self, ctx):        
        hope_path = os.path.abspath('./assets/feels/hope/hope.jpg') 
        await ctx.send(content=f"{ctx.author.mention} Have hope my fellow kings!", file=discord.File('{}'.format(hope_path)))

    @commands.command()
    async def pain(self, ctx):

        # TODO: Same as above section, move this to the config. 
        responses = ["**DON'T CALL IT A GRAVE, IT'S THE FUTURE YOU CHOSE**", "**THE BELLS TOLL FOR THEE**",
                     "**WHEN WILL YOU LEARN THAT YOUR ACTIONS HAVE CONSEQUENCES**", "**THE ABYSS HAS FINALLY STARED BACK**"]
        fileUpload = random.choice(os.listdir("./assets/feels/pain/"))
        await ctx.send(content=f"{random.choice(responses)}", file=discord.File(f'assets/feels/pain/{fileUpload}'))

    @commands.command()
    async def lol(self, ctx):
        # TODO: 
        vid = random.choice(os.listdir("assets/lol/"))
        await ctx.send(content=f'', file=discord.File(f'assets/lol/{vid}'))

    @commands.command()
    async def kino(self, ctx, *,input): # FIXME: Add new logic to determine which link to post to the chat!

        #! Broken, fix later or remove.
        if 'joker' in input.lower():
            await ctx.send('SOCIETY\nhttps://cdn.discordapp.com/attachments/699151253321547857/710905743808659486/joker_movie.webm')
        #! Broken, fix later or remove.
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

    @commands.command(aliases=['feedandseed','chuck','fuckandsuck'], name="sneed", brief="Randomly selects a Sneed image for the user.")
    async def sneed(self, ctx):
        try:
            sneedImg = random.choice(os.listdir("assets/sneed/"))
            await ctx.send(content=f'', file=discord.File(f'assets/sneed/{sneedImg}'))
        except Exception as e:
            print(e)

    #! Enforce char limit, look into later, low priority. 
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
        result = get_best_definition(query)
        try:
            embed = discord.Embed(title=f'__**{query}**__', description=f'__Definition:__\n{best_definition}\n\n__Example:__\n*{best_example}*')
            await ctx.send(embed=embed)
        except Exception as e:
            #await ctx.send(f":warning: {ctx.author.mention} Couldn't find word term : {query}")
            await ctx.send(f"{e}")

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

async def setup(bot):
  await bot.add_cog(Recreational(bot))
