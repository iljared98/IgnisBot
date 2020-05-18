import discord
import random
import os
from random import randint
from discord.ext import commands

class funCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    # FIXME: Expand functionality with betting and passing the gun to other users
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
        await ctx.send(f'You rolled: {rollVal}!')

    @commands.command(aliases=['8ball'])
    async def _8ball(self, ctx, *, question):
        responseList = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes - definitely.',
                        'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                        'Signs point to yes.', 'Reply hazy, try again later.', 'Ask another time.',
                        "Don't ask questions you don't want to know the answer to.", 'Cannot predict now.',
                        'Ask your mother.', "Don't count on it.", 'My reply is no.', 'My sources say no.',
                        'Outlook not so good.', 'Very doubtful.']
        await ctx.send(f'Question: {question}\nAnswer: {random.choice(responseList)}')

    @commands.command()
    async def hope(self, ctx):

        #FIXME: Add regex or some other check to allow hope PNG/JPG and no other filetypes!
        hope_path = os.path.abspath('assets/feels/hope.jpg') # Change to relative path
        await ctx.send(content="Have hope my fellow kings!", file=discord.File('{}'.format(hope_path)))

    @commands.command()
    async def pain(self, ctx):
        # FIXME: Add regex or some other check to allow hope PNG/JPG and no other filetypes!
        pain_path = os.path.abspath('assets/feels/pain.jpg') # Change to relative path
        await ctx.send(content="DON'T CALL IT A GRAVE, IT'S THE FUTURE YOU CHOSE",
                       file=discord.File('{}'.format(pain_path)))

    @commands.command()
    async def lol(self, ctx):
        lolPath = os.path.abspath('assets/lol/') # Change to relative path
        lolExt = (".mp4", ".webm")
        lolList = []
        for file in os.listdir(lolPath):
            if file.endswith(lolExt):
                lolList.append(os.path.join(lolPath, file))

        lolChosen = random.choice(lolList)
        await ctx.send(file=discord.File('{}'.format(lolChosen)))

    # FIXME: Add this to the kino command later, let the users search by keyword
    @commands.command()
    async def spangbab(self, ctx):
        krabsPiracy = ["Ahoy SpongeBob me boy, piracy is illegal in the United States of America! ARGH ARGH ARGH ARGH!",
                       "Ahoy SpongeBoy me Bob, I am going to get sued by Viacom for posting the full SpongeBob movie! ARGH ARGH ARGH ARGH!",
                       "Ahoy SpongeBob me boy, I found a shitty camera rip of the original SpongeBob movie! ARGH ARGH ARGH ARGH!"]
        krabsPiracyResponse = random.choice(krabsPiracy)
        await ctx.send(
            f"{krabsPiracyResponse}\n https://cdn.discordapp.com/attachments/581533299491733570/632748985022414878/spongebob_first_movie.mp4")

        # Joker : https://cdn.discordapp.com/attachments/699151253321547857/710905743808659486/joker_movie.webm







def setup(client):
  client.add_cog(funCommand(client))