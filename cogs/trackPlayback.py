import typing as t
import wavelink
import discord
import asyncio
import re
import random
import datetime as dt
from discord.ext import commands
from enum import Enum

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class NoTracks(commands.CommandError):
    pass

class AlreadyConnected(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueEmpty(commands.CommandError):
    pass

class PlayerAlreadyPaused(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueEmpty

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueEmpty

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def empty(self):
        self._queue.clear()

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueEmpty

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL


class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnected

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracks

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)

        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f'Added {tracks[0].title}') # use embed later
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                #FIXME: Add embed here.
                #embed = discord.Embed(title=f'{track.title}', description=f'hhhhhhhhhh')
                #embed.set_author(name="Requested Track")
                #
                await ctx.send(f'Added {track.title}')

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5]) # increase to the max of 10
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]


    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
        except QueueEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)



class Playback(commands.Cog, wavelink.WavelinkMixin):
    """Commands involving voice channels and audio playback."""

    def __init__(self, client):
        self.client = client
        self.wavelink = wavelink.Client(bot=client)
        self.client.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await asyncio.sleep(15)
                await self.get_player(member.guild).teardown()



    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f'Wavelink node {node.identifier} ready.')

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send(f":warning: {ctx.author.mention} **Music commands not available in direct messages.**")
            return False

        return True

    async def start_nodes(self):
        await self.client.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "us_central",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"Connected to {channel.name}.")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnected):
            await ctx.send(f":warning: {ctx.author.mention} **Already connected to a voice channel.**")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send(f":warning: {ctx.author.mention} **No suitable voice channel was provided.**")

    @commands.command(name="disconnect", aliases=["leave"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send(f"**Disconnecting from Voice.**")

    @commands.command(name="play", aliases=['p', 'pla'])
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueEmpty

            await player.set_pause(False)
            await ctx.send(f"{ctx.author.mention} **Playback resumed.**")


        else:
            query = query.strip("<link>")
            if not re.match(URL_REGEX, query):
                query = f'ytsearch:{query}'

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query)) #check this

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueEmpty):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks to play: empty queue.**")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send(f":warning: {ctx.author.mention} **No suitable voice channel was provided.**")


    @commands.command(name="pause")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)
        if player.is_paused:
            raise PlayerAlreadyPaused

        await player.set_pause(True)
        await ctx.send(f"{ctx.author.mention} **Pausing playback.**")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerAlreadyPaused):
            await ctx.send(f":warning: {ctx.author.mention} **Voice player is already paused.**")


    @commands.command(name="stop")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send(f"{ctx.author.mention} Playback has stopped.")

    @commands.command(name="next", aliases=['skip','sk'])
    async def skip_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send(f"{ctx.author.mention} **Skipping to next track.**")

    @skip_command.error
    async def skip_command_error(self, ctx, exc):
        if isinstance(exc, QueueEmpty):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks in queue to skip.**")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks in queue to skip.**")

    @commands.command(name="previous", aliases=['back','prev'])
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send(f"{ctx.author.mention} **Going to previous track.**")

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueEmpty):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks to backtrack to.**")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks to backtrack to.**")

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send(f"{ctx.author.mention} **Shuffling current queue.**")


    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueEmpty):
            await ctx.send(f":warning: {ctx.author.mention} **There are no tracks to backtrack to.**")




    @commands.command(name="repeat")
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send(f'{ctx.author.mention} **Repeat mode has been set to : {mode}**')




    @commands.command(name="queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueEmpty

        embed = discord.Embed(
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Queue") #FIXME: Add more features to this embed.
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Currently playing", value=getattr(player.queue.current_track, "title", f":warning: {ctx.author.mention} **No tracks currently playing.**"), inline=False)
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Upcoming",
                value="\n".join(t.title for t in upcoming[:show]),
                inline=False
            )

        msg = await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueEmpty):
            await ctx.send(f":warning: {ctx.author.mention} **The queue is currently empty.**")


def setup(client):
    client.add_cog(Playback(client))