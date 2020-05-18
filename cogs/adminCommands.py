import discord
from discord.ext import commands
from discord.ext.commands import has_permissions


class adminCommand(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(aliases=['cc'])
    @has_permissions(manage_messages=True)
    async def clearchat(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'Member {member.mention} has been kicked for: {reason}!')

    @commands.command()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'Member {member.mention} has been banned for: {reason}!')

    @commands.command()
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Member {member.mention} has been unbanned!')
                return

    @commands.command(aliases=['dc', 'disconnect'])
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send(f'IgnisBot is going offline for maintenance. :wave:')
        await self.client.logout()

    @logout.error
    async def logout_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'You do not have permission to use this command!')
        else:
            raise error

def setup(client):
  client.add_cog(adminCommand(client))