from collections import deque
from datetime import timedelta
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}
        self.current_song = {}  
        self.queues = {}

    async def join(self, ctx):
        """Join the voice channel."""
        if ctx.author.voice is None:
            embed = discord.Embed(
                    title='Join Command Error',
                    description="❌ You need to be in a voice channel to use this command.",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            await ctx.send(ctx.author.mention, embed=embed)
            return False
            
        channel = ctx.author.voice.channel
        guild_id = ctx.guild.id
        
        
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            await self.voice_clients[guild_id].move_to(channel)
        else:
            self.voice_clients[guild_id] = await channel.connect()
            
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
            
        return True

    async def leave(self, ctx):
        """Leave the voice channel."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            await self.voice_clients[guild_id].disconnect()
            del self.voice_clients[guild_id]
            if guild_id in self.current_song:
                del self.current_song[guild_id]

            if guild_id in self.queues:
                self.queues[guild_id].clear()
            return True
        return False

    async def play(self, ctx, url):
        """Play a song or add it to the queue."""
        guild_id = ctx.guild.id
        
        if guild_id not in self.voice_clients or not self.voice_clients[guild_id].is_connected():
            success = await self.join(ctx)
            if not success:
                return
        
        voice_client = self.voice_clients[guild_id]
        
        if voice_client.is_playing() or voice_client.is_paused():
            await self._add_to_queue(ctx, url)
            return
        
        await self._play_song(ctx, url)
    
    async def _extract_info(self, url):
        """Extract audio info with multiple format fallbacks."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'source_address': '0.0.0.0',
        }
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            if "Requested format is not available" in str(e):
                ydl_opts['format'] = 'best'
                try:
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        return info
                except Exception:
                    del ydl_opts['format']
                    try:
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=False)
                            return info
                    except Exception:
                        minimal_opts = {
                            'quiet': True,
                            'no_warnings': True,
                        }
                        try:
                            with youtube_dl.YoutubeDL(minimal_opts) as ydl:
                                info = ydl.extract_info(url, download=False)
                                return info
                        except Exception as e:
                            raise Exception(f"Failed to extract info after multiple attempts: {str(e)}")
            else:
                raise

    async def _get_audio_url(self, info):
        """Get the best available audio URL from info dict."""
        if 'url' in info:
            return info['url']
        
        if 'formats' in info and info['formats']:
            audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            if audio_formats:
                return audio_formats[0]['url']
            
            for fmt in info['formats']:
                if 'url' in fmt:
                    return fmt['url']

        raise Exception("Could not find a playable audio URL in the video information")

    async def _add_to_queue(self, ctx, url):
        """Add a song to the queue."""
        guild_id = ctx.guild.id
        embed = discord.Embed(
                    title='Searching for Track',
                    description=f"🔍 Fetching song info for queue\n`{url}`",
                    color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        message = await ctx.send(ctx.author.mention, embed=embed)

        try:
            info = await self._extract_info(url)

            if 'entries' in info:  
                info = info['entries'][0]

            audio_url = await self._get_audio_url(info)

            song_info = {
                'title': info.get('title', 'Unknown title'),
                'url': url,
                'audio_url': audio_url,
                'duration': info.get('duration', 0),
                'requester': ctx.author.name
            }

            self.queues[guild_id].append(song_info)

            duration_str = str(timedelta(seconds=song_info['duration'])) if song_info['duration'] else "Unknown"
            position = len(self.queues[guild_id])

            embed = discord.Embed(
                    title='Successfully Found Song',
                    description=f"✅ Added to queue (#{position}):\n**{song_info['title']}**\n`{duration_str}`",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await message.edit(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                    title='Error Adding to Queue',
                    description=f"❌ An error has occurred while adding your song to the queue:\n`{str(e)}`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await message.edit(embed=embed)

    async def _play_song(self, ctx, url=None, song_info=None):
        """Play a song from URL or song_info."""
        guild_id = ctx.guild.id
        voice_client = self.voice_clients[guild_id]

        if not song_info:
            embed = discord.Embed(
                    title='Searching for Track',
                    description=f"🔍 Fetching song info for queue\n`{url}`",
                    color=discord.Color.yellow()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            message = await ctx.send(ctx.author.mention, embed=embed)

            try:
                info = await self._extract_info(url)

                if 'entries' in info: 
                    info = info['entries'][0]

                audio_url = await self._get_audio_url(info)

                song_info = {
                    'title': info.get('title', 'Unknown title'),
                    'url': url,
                    'audio_url': audio_url,
                    'duration': info.get('duration', 0),
                    'requester': ctx.author.name
                }

                await message.edit(content=f"🎵 Preparing to play: **{song_info['title']}**")

            except Exception as e:
                if message:
                    await message.edit(content=f"❌ Error: {str(e)}")
                print(f"Error extracting song info: {e}")
                return
        
        try:
            self.current_song[guild_id] = song_info

            # Set options like this in case of connectivity issues.
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -bufsize 1M'
            }

            voice_client.play(
                discord.FFmpegPCMAudio(song_info['audio_url'], **ffmpeg_options),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self._after_play(ctx, e, guild_id), self.bot.loop
                )
            )

            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=0.5)

            duration_str = str(timedelta(seconds=song_info['duration'])) if song_info['duration'] else "Unknown"
            embed = discord.Embed(
                    title='Playing Track',
                    description=f"🎵 Now playing: **{song_info['title']}**\n`{duration_str}`\n(Requested by: {song_info['requester']})",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

        except Exception as e:
            embed = discord.Embed(
                    title='Could Not Play Song',
                    description=f"❌ Error playing song:\n`{str(e)}`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            await self._play_next(ctx, guild_id)

    async def _after_play(self, ctx, error, guild_id):
        """Callback after a song finishes playing."""
        if error:
            embed = discord.Embed(
                    title='Playback Error',
                    description=f"❌ Error occurred during playback: {error}`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        
        if guild_id in self.current_song:
            del self.current_song[guild_id]
            
        await self._play_next(ctx, guild_id)

    async def _play_next(self, ctx, guild_id):
        """Play the next song in the queue if available."""
        if guild_id not in self.queues or not self.queues[guild_id] or guild_id not in self.voice_clients:
            return
            
        if not self.voice_clients[guild_id].is_connected():
            return
            
        next_song = self.queues[guild_id].popleft()
        
        await self._play_song(ctx, song_info=next_song)

    @commands.command(name='join')
    async def join_command(self, ctx):
        """Command to make the bot join the voice channel."""
        if await self.join(ctx):
            embed = discord.Embed(
                    title='IgnisBot Joined Channel',
                    description=f"👋 Joined channel:\n`{ctx.author.voice.channel.name}`",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='leave')
    async def leave_command(self, ctx):
        """Command to make the bot leave the voice channel."""
        if await self.leave(ctx):
            embed = discord.Embed(
                    title='IgnisBot Left Channel',
                    description=f"👋 Left the voice channel:\n`{ctx.author.voice.channel.name}`",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='IgnisBot Not in a Channel',
                    description=f"❌ I'm not in a voice channel",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='play')
    async def play_command(self, ctx, *, url):
        """Command to play audio from a YouTube URL or add it to the queue."""
        await self.play(ctx, url)

    @commands.command(name='skip')
    async def skip_command(self, ctx):
        """Command to skip the current song."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            embed = discord.Embed(
                    title='Skipping Song',
                    description=f"⏭️ Skipped the current song",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Playing',
                    description=f"❌ Nothing is playing right now",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='stop')
    async def stop_command(self, ctx):
        """Command to stop playback and clear the queue."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            if guild_id in self.queues:
                self.queues[guild_id].clear()
            embed = discord.Embed(
                    title='Playback Stopped',
                    description=f"⏹️ Stopped playback and cleared the queue",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Playing',
                    description=f"❌ Nothing is playing right now",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='pause')
    async def pause_command(self, ctx):
        """Pause the current playback."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].pause()

            embed = discord.Embed(
                    title='Song Paused',
                    description=f"⏸️ Paused the playback",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Playing',
                    description=f"❌ Nothing is playing right now",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='resume')
    async def resume_command(self, ctx):
        """Resume the paused playback."""
        guild_id = ctx.guild.id
        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_paused():
            self.voice_clients[guild_id].resume()
            embed = discord.Embed(
                    title='Song Resumed',
                    description=f"▶️ Resumed the playback",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='Song Pause Error',
                    description=f"❌ Playback is not paused",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='volume', aliases=['vol'])
    async def volume_command(self, ctx, volume: int = None):
        """Change the playback volume (0-100)."""
        guild_id = ctx.guild.id

        if volume is None:
            if guild_id in self.voice_clients and self.voice_clients[guild_id].source:
                current_vol = int(self.voice_clients[guild_id].source.volume * 100)
                embed = discord.Embed(
                    title='Player Volume',
                    description=f"🔊 Current volume: {current_vol}%",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(ctx.author.mention, embed=embed)
            else:
                embed = discord.Embed(
                    title='No Songs Playing',
                    description="❌ Nothing is playing right now",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(ctx.author.mention, embed=embed)
            return

        if volume < 0 or volume > 100:
            embed = discord.Embed(
                    title='Volume Command Error',
                    description=f"❌ Volume must be between 0 and 100 (integer)",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if guild_id in self.voice_clients and self.voice_clients[guild_id].source:
            self.voice_clients[guild_id].source.volume = volume / 100
            embed = discord.Embed(
                    title='Player Volume Adjust',
                    description=f"🔊 Volume set to {volume}%",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Playing',
                    description=f"❌ Nothing is playing right now",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='np', aliases=['nowplaying'])
    async def now_playing_command(self, ctx):
        """Show what song is currently playing."""
        guild_id = ctx.guild.id
        if guild_id in self.current_song:
            song = self.current_song[guild_id]
            duration_str = str(timedelta(seconds=song.get('duration', 0))) if song.get('duration') else "Unknown"
            embed = discord.Embed(
                    title='Song Playing',
                    description=f"🎵 Now playing:\n**{song['title']}**\n`[{duration_str}]`\n(Requested by: {song['requester']})",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Playing',
                    description=f"❌ Nothing is playing right now",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='queue', aliases=['q'])
    async def queue_command(self, ctx):
        """Show the current queue."""
        guild_id = ctx.guild.id
        if not guild_id in self.queues or len(self.queues[guild_id]) == 0:
            embed = discord.Embed(
                    title='No Songs Queued',
                    description=f"📋 The queue is empty",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.green())

        if guild_id in self.current_song:
            song = self.current_song[guild_id]
            duration_str = str(timedelta(seconds=song.get('duration', 0))) if song.get('duration') else "Unknown"
            embed.add_field(
                name="Now Playing", 
                value=f"**{song['title']}** [{duration_str}] - Requested by: {song['requester']}", 
                inline=False
            )

        queue_text = ""
        total_duration = 0

        for i, song in enumerate(self.queues[guild_id], 1):
            duration = song.get('duration', 0)
            total_duration += duration
            duration_str = str(timedelta(seconds=duration)) if duration else "Unknown"
            
            entry = f"`{i}.` **{song['title']}** [{duration_str}] - Requested by: {song['requester']}\n"
            
            # Discord has a field value limit of 1024 characters
            if len(queue_text + entry) > 1000:
                queue_text += f"And {len(self.queues[guild_id]) - i + 1} more songs..."
                break
                
            queue_text += entry

        if queue_text:
            embed.add_field(name="Up Next", value=queue_text, inline=False)

        total_duration_str = str(timedelta(seconds=total_duration)) if total_duration else "Unknown"
        embed.set_footer(text=f"Total songs in queue: {len(self.queues[guild_id])} | Total duration: {total_duration_str}")

        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='clear')
    async def clear_command(self, ctx):
        """Clear the music queue."""
        guild_id = ctx.guild.id
        if guild_id in self.queues:
            queue_length = len(self.queues[guild_id])
            self.queues[guild_id].clear()
            embed = discord.Embed(
                    title='Queue Cleared',
                    description=f"🗑️ Cleared {queue_length} songs from the queue",
                    color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        else:
            embed = discord.Embed(
                    title='No Songs Queued',
                    description="📋 The queue is already empty",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name='remove')
    async def remove_command(self, ctx, position: int):
        """Remove a specific song from the queue."""
        guild_id = ctx.guild.id
        if guild_id not in self.queues or len(self.queues[guild_id]) == 0:
            embed = discord.Embed(
                    title='No Songs Queued',
                    description="📋 The queue is empty",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if position < 1 or position > len(self.queues[guild_id]):
            embed = discord.Embed(
                    title='Invalid Song Position',
                    description=f"❌ Invalid position. Please use a number between `1 and {len(self.queues[guild_id])}`",
                    color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return
            
        position -= 1
        removed_song = list(self.queues[guild_id])[position]
        new_queue = deque()
        
        for i, song in enumerate(self.queues[guild_id]):
            if i != position:
                new_queue.append(song)
                
        self.queues[guild_id] = new_queue
        embed = discord.Embed(
                    title='Song Removed',
                    description=f"🗑️ Removed **{removed_song['title']}** from the queue",
                    color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(ctx.author.mention, embed=embed)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))