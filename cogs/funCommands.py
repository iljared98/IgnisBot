import os
import random
from random import randint
import re
import urllib.parse
import urllib.request
import toml
import discord
from discord.ext import commands
from modules.urbandictionary import get_best_definition
from modules.russ_roulette import get_balance, update_balance

config = toml.load("config.toml")

class Recreational(commands.Cog):

    """Commands for user entertainment."""

    def __init__(self, bot):
        self.bot = bot

    #! Rework this later.
    @commands.command()
    async def russrul(self, ctx):
        chambers = [1, 2, 3, 4, 5, 6]
        bang = random.choice(chambers)
        pull = random.choice(chambers)
        if bang != pull:
            await ctx.send(f'*Click!* {ctx.author.mention} has survived!')
        elif bang == pull:
            await ctx.send(f'*BANG!* {ctx.author.mention} has died!')



    @commands.command()
    async def roll(self, ctx, roll_min: int, roll_max: int):
        """Generate a random number between specified bounds.
    
        :param ctx: Discord command context
        :type ctx: discord.ext.commands.Context
        :param roll_min: Minimum value (inclusive) for random roll
        :type roll_min: int
        :param roll_max: Maximum value (inclusive) for random roll
        :type roll_max: int
        
        :returns: None
        :rtype: None
        
        :note:

            - Uses cryptographically secure random number generation
            - Both bounds are inclusive
            - Displays result in an embed with user's avatar
        
        :example:
            
            -roll 1 20  # Rolls between 1-20 inclusive
        """
        roll_val = randint(roll_min, roll_max)
        embed = discord.Embed(
                title='IgnisBot Dice Roll',
                description=f"{ctx.author.name} rolled a {roll_val}!",
                color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(f"{ctx.author.mention}", embed=embed)

    @roll.error
    async def roll_error(self, ctx, error):
        """Handle errors for the roll command.
    
        :param ctx: Discord command context
        :type ctx: discord.ext.commands.Context
        :param error: The exception that was raised
        :type error: Exception
        
        :returns: None
        :rtype: None
        
        :handles:

            - :class:`commands.MissingRequiredArgument`: When arguments are missing
            - :class:`commands.BadArgument`: When invalid types are provided
            - All other exceptions with generic error message
        
        :note:

            - Provides example usage in error messages
            - Maintains consistent embed styling
            - Always pings the command invoker
        """
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                    title='ROLL ERROR',
                    description="⚠️ You need to provide both minimum and maximum numbers.\nExample: `-roll 1 100`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                    title='ROLL ERROR',
                    description="⚠️ You provided an invalid data type, both inputs must be integers.\nExample: `-roll 1 100`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)
        else:
            embed = discord.Embed(
                    title='ROLL ERROR',
                    description=f"⚠️ An unspecified error has occurred.\n`{error}`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)
            
        

    #! Prettify this (and roll command), maybe toss them in embeds?
    @commands.command(name='8ball')
    async def magic_8ball(self, ctx, *, question):
        if len(question) == 0:
            embed = discord.Embed(

            )
            await ctx.send(f':warning: {ctx.author.mention} Cannot predict off of a blank input.', delete_after=15)
        else:
            embed = discord.Embed(

            )
            response_list = config["MAGIC_8BALL_RESPONSES"]
            await ctx.send(f'{ctx.author.mention}  Question: {question}\nAnswer: {random.choice(response_list)}')

    @commands.command(name='hope')
    async def hope_image(self, ctx):  
        hope_path = os.path.abspath('./assets/feels/hope/hope.jpg') 
        await ctx.send(content=f"{ctx.author.mention} Have hope my fellow kings!", file=discord.File('{}'.format(hope_path)))

    @commands.command(name='pain')
    async def pain_image(self, ctx):
        responses = config['PAIN_IMG_RESPONSES']
        file_upload = random.choice(os.listdir("./assets/feels/pain/"))
        await ctx.send(content=f"{random.choice(responses)}", file=discord.File(f'assets/feels/pain/{file_upload}'))

    @commands.command()
    async def lol(self, ctx):
        # TODO: 
        vid = random.choice(os.listdir("assets/lol/"))
        await ctx.send(file=discord.File(f'assets/lol/{vid}'))

    @commands.command()
    async def kino(self, ctx, *, query): # FIXME: Add new logic to determine which link to post to the chat!
        #! Broken, fix later or remove.
        try:
            kino_dict = config["kino_dict"]
            for pattern in kino_dict.values():
                if re.search(pattern['regex'], query):
                    selected_msg = random.choice(pattern['msgContents'])
                    result = pattern['url'] + " " + selected_msg
                else:
                    await ctx.send(':warning: Your search did not come up with any results, please try again!')

            await ctx.send(f"{result}")
        except Exception:
            await ctx.send(':warning: Your search did not come up with any results, please try again!')


    @commands.command(aliases=['chokememe'])
    async def choke(self, ctx):
        """ Displays a meme edit of the notorious TLOU2 choke scene. """
        try:
            choke_img = random.choice(os.listdir("assets/choke/"))
            await ctx.send(file=discord.File(f'assets/choke/{choke_img}'))
        except:
            print('CHOKE ERROR')

    @commands.command(name='sneed', aliases=['feedandseed','chuck','fuckandsuck'], brief="Randomly selects a Sneed image for the user.")
    async def sneed_image(self, ctx):
        try:
            sneedImg = random.choice(os.listdir("assets/sneed/"))
            await ctx.send(file=discord.File(f'assets/sneed/{sneedImg}'))
        except Exception as e:
            print(e)

    #! Command by Nicolas Hickson (2019)
    #! Relatively unmodified beyond minor changes.
    @commands.command()
    async def ascii_movie(self, ctx, *args):
        join_args = ' '.join(args)
        if '|' not in args:
            join_args += '|'
            join_args += ''
        lines = join_args.split('|')
        if len(lines) > 2:
            embed = discord.Embed(
                    title='ASCII MOVIE ERROR',
                    description="⚠️ Too many lines given. Marquee can have a maximum of 2 lines.",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)
        else:
            if len(lines[0]) > 29 or len(lines[1]) > 29:
                embed = discord.Embed(
                    title='ASCII MOVIE ERROR',
                    description="⚠️ The marquee title / subtitle can only be a maximum of 29 characters.",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(f"{ctx.author.mention}", embed=embed)

            else:
                x = 29 - len(lines[0].strip())
                y = 29 - len(lines[1].strip())
                space_x = ' ' * int(x / 2)
                space_y = ' ' * int(y / 2)
                fin_message_x = f'{space_x}{lines[0].upper().strip()}{space_x}'
                fin_message_y = f'{space_y}{lines[1].upper().strip()}{space_y}'
                if len(fin_message_x) != 30:
                    while len(fin_message_x) != 30:
                        fin_message_x += ' '
                if len(fin_message_y) != 30:
                    while len(fin_message_y) != 30:
                        fin_message_y += ' '

                # Leaving this string as is
                await ctx.send(f"""```
                          @-_________________-@
                    @-_____|   NOW SHOWING   |______-@
                     |{fin_message_x}|
                     |{fin_message_y}|
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

    @commands.command(name='urbandictionary', aliases=['urban','ud'])
    async def urbandictionary_command(self, ctx, *args):
        try:
            query = str(' '.join(args))

            # Because this function returns a tuple I had to define these vars this way.
            best_definition, best_example = get_best_definition(query)

            # Urban D keeps putting brackets into the output strings on the embed, removing them.
            best_definition = best_definition.replace("[", "").replace("]", "")
            best_example = best_example.replace("[", "").replace("]", "")

            embed = discord.Embed(
                title=f'__**{query}**__', 
                description=f'__Definition:__\n{best_definition}\n\n__Example:__\n*{best_example}*',
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                title='URBAN DICTIONARY ERROR',
                description=f"⚠️ Your search query does not exist or something went wrong on Urban Dictionary's end. Please try again later.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(f"{ctx.author.mention}", embed=embed)

    @commands.command(aliases=['ytsearch'])
    async def youtube(self, ctx, *, query):
        try:
            search = urllib.parse.urlencode({
                'search_query' : query
            })
            content = urllib.request.urlopen('https://www.youtube.com/results?' + search)
            results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            await ctx.send('https://youtube.com/watch?v=' + results[0])

        except:
            await ctx.send(f':warning: {ctx.author.mention} **Video could not be found/processed.**')

async def setup(bot):
    await bot.add_cog(Recreational(bot))
