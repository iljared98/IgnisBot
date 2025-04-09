import discord
from discord.ext import commands
import os
from urllib import request
from urllib.request import Request, urlopen
import time
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs
import asyncio
import toml
import yt_dlp
from modules.media_downloader import download_video, compress_video, convert_to_gif

config = toml.load("config.toml")
BOT_EMBED_THUMBNAIL = config["BOT_EMBED_THUMBNAIL"]



class downloadStreamCommands(commands.Cog):
    """Commands involving downloading files, web scraping, and streaming video."""
    def __init__(self, bot):
        self.bot = bot

    #! Originally contributed by Nic Hickson (2019), has been updated since due to
    #! yt-dlp superceding YoutubeDL, and for the new API changes.
    @commands.command(name="ytinfo")
    async def ytInfo(self, ctx, *, URL=None):
        if URL is None:
            embed = discord.Embed(
                title='No URL Provided',
                description='❌ Please provide a YouTube URL',
                color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            return
        
        url_parts = URL.split()
        actual_url = url_parts[0]
        args = url_parts[1:] if len(url_parts) > 1 else []
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'skip_download': True,  
            'ignoreerrors': True   
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                meta = ydl.extract_info(actual_url, download=False)
            
            if not meta:
                embed = discord.Embed(
                    title='Generic Error',
                    description=f'❌ Could not retrieve information for the URL: {actual_url}',
                    color=discord.Color.red()
                )
                embed.set_thumbnail(ctx.author.display_avatar.url)
                await ctx.send(ctx.mention, embed=embed)
                return
            
            if 'entries' in meta:
                meta = meta['entries'][0]
                if not meta:
                    embed = discord.Embed(
                        title='Playlist Error',
                        description=f'❌ Could not retrieve information from the playlist entry.',
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(ctx.author.display_avatar.url)
                    await ctx.send(ctx.mention, embed=embed)
                    return
            
            upload_date = meta.get('upload_date')
            post_date = f'{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}' if upload_date else 'Unknown'
            duration = meta.get('duration', 0)
            
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
                    title = meta.get('title', 'Unknown Title'),
                    description = meta.get('description', 'No description available'),
                    colour = discord.Colour.red()
                )
            else:
                embed = discord.Embed(
                    title = meta.get('title', 'Unknown Title'),
                    colour = discord.Colour.green()
                )
                
                thumbnail = meta.get('thumbnail')
                if thumbnail:
                    embed.set_image(url=thumbnail)
                    
                embed.add_field(name='Upload Date', value=post_date, inline=True)
                embed.add_field(name='Views', value=format(meta.get('view_count', 0), ',d'), inline=True)
                embed.add_field(name='Video Duration', value=finalDur, inline=True)
                embed.add_field(name='Likes', value=format(meta.get('like_count', 0), ',d'), inline=True)
                
                embed.add_field(name='Author', value=meta.get('uploader', 'Unknown'), inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title='Error: Info Grab Failed',
                description='❌ Error retrieving video information:\n`{str(e)}`',
                color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)


    @commands.command()
    async def vidgrab(self, ctx, url: str):
      embed = embed(
        title='Queueing Video',
        description='Processing your video download... this may take a moment.',
        color=discord.Color.yellow()
      )
      embed.set_thumbnail(ctx.author.display_avatar.url)
      await ctx.send(ctx.mention, embed=embed)

      loop = asyncio.get_event_loop()
      video_path = await loop.run_in_executor(None, download_video, url)

      if video_path == "TOO_LARGE":
          embed = discord.Embed(
            title='Error: File Too Large',
            description='❌ The video is too large to be sent on Discord.',
            color=discord.Color.red()
          )
          embed.set_thumbnail(ctx.author.display_avatar.url)
          await ctx.send(ctx.mention, embed=embed)
      elif video_path:
          embed = discord.Embed(
            title='Succesful Video Grab',
            description='✅ Here is your video.',
            color=discord.Color.green()
          )
          embed.set_thumbnail(ctx.author.display_avatar.url)
          await ctx.send(ctx.mention, embed=embed, file=discord.File(video_path))
          os.remove(video_path)
      else:
          embed = discord.Embed(
            title='Error: Download Failed',
            description='❌ Failed to download the video.',
            color=discord.Color.red()
          )
          embed.set_thumbnail(ctx.author.display_avatar.url)
          await ctx.send(ctx.mention, embed=embed)

    @commands.command()
    async def gifconvert(self, ctx, url: str = None):
        """Convert a video (from URL or uploaded file) to a GIF."""
        ALLOWED_GIFCONVERT_EXTENSIONS = [ext.lower() for ext in config.get("ALLOWED_GIFCONVERT_EXTENSIONS", [])]
        
        if url and ctx.message.attachments:
            embed = discord.Embed(
                title='Error: Bad Input',
                description='❌ Please provide either a URL or a file upload, not both.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            return
        
        video_path = None

        if url:
            embed = embed(
                title='Queuing GIF Conversion',
                description='Downloading video... please wait.',
                color=discord.Color.yellow()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(None, download_video, url)

            if video_path:
                file_extension = os.path.splitext(video_path)[1].lower()
                if file_extension not in ALLOWED_GIFCONVERT_EXTENSIONS:
                    os.remove(video_path)
                    embed = discord.Embed(
                        title='Error: Bad File Type',
                        description='❌ Invalid video format. Only `MP4, WEBM, and MOV` are supported.',
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(ctx.author.display_avatar.url)
                    await ctx.send(ctx.mention, embed=embed)
                    return

        elif ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            file_extension = os.path.splitext(attachment.filename)[1].lower()


            if file_extension not in ALLOWED_GIFCONVERT_EXTENSIONS:
                embed = discord.Embed(
                    title='Error: Bad File Type',
                    description='❌ Invalid video format. Only `MP4, WEBM, and MOV` are supported.',
                    color=discord.Color.red()
                )
                embed.set_thumbnail(ctx.author.display_avatar.url)
                await ctx.send(ctx.mention, embed=embed)
                return

            embed = embed(
                title='Queuing GIF Conversion',
                description='Downloading video... please wait.',
                color=discord.Color.yellow()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            video_path = await self.download_attachment(attachment)

        else:
            embed = discord.Embed(
                title='Error: Bad Input',
                description='❌ You must provide either a URL or upload a video file.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            return

        if not video_path:
            embed = discord.Embed(
                        title='Error: Could not Process',
                        description='❌ Failed to process the video.',
                        color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)
            return

        loop = asyncio.get_event_loop()
        gif_path = await loop.run_in_executor(None, convert_to_gif, video_path)

        if gif_path:
            embed = discord.Embed(
                title='Succesful GIF Convert',
                description='✅ Here is your GIF.',
                color=discord.Color.green()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed, file=discord.File(gif_path))
            os.remove(gif_path)  
            os.remove(video_path) 
        else:
            embed = discord.Embed(
                title='Error: Conversion Failed',
                description='❌ Failed to convert video to a GIF.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(ctx.author.display_avatar.url)
            await ctx.send(ctx.mention, embed=embed)


    async def download_attachment(self, attachment):
        VIDEO_DOWNLOAD_DIR = "downloads"
        os.makedirs(VIDEO_DOWNLOAD_DIR, exist_ok=True)

        file_path = os.path.join(VIDEO_DOWNLOAD_DIR, attachment.filename)

        try:
            await attachment.save(file_path)
            return file_path
        except Exception as e:
            return None


async def setup(bot):
  await bot.add_cog(downloadStreamCommands(bot))
