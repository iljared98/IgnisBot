import os
import asyncio
import toml
import discord
from discord.ext import commands
import yt_dlp
from modules.media_downloader import download_video, convert_to_gif

config = toml.load("config.toml")

class DownloadStreamCommands(commands.Cog):
    """Commands involving downloading files, web scraping, and streaming video."""
    def __init__(self, bot):
        self.bot = bot

    #! Originally contributed by Nic Hickson (2019), has been updated since due to
    #! yt-dlp superceding YoutubeDL, and for the new API changes.
    @commands.command(name="ytinfo")
    async def yt_info(self, ctx, *, URL=None):
        """Fetch and display YouTube video metadata in Discord.
    
        Retrieves video information including title, description, view count, duration,
        and other metadata using yt-dlp. Supports both regular videos and playlist entries.

        :param ctx: Discord command context
        :type ctx: discord.ext.commands.Context
        :param URL: YouTube URL to analyze (supports additional arguments)
        :type URL: str | None

        :returns: None

        :rtype: None

        :raises:
        
            - yt_dlp.DownloadError: If video info extraction fails
            - discord.HTTPException: If Discord API operations fail

        :note:

            - Supports playlist entries (first video only)
            - Additional arguments:
            - 'desc' - Includes video description in output
            - Automatically formats:
            - View/like counts with thousands separators
            - Upload dates (YYYY-MM-DD)
            - Video duration (HH:MM:SS or MM:SS)

        :example:

            -ytinfo https://youtu.be/dQw4w9WgXcQ
        """
        if URL is None:
            embed = discord.Embed(
                title='No URL Provided',
                description='❌ Please provide a YouTube URL',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
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
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(ctx.author.mention, embed=embed)
                return
            
            if 'entries' in meta:
                meta = meta['entries'][0]
                if not meta:
                    embed = discord.Embed(
                        title='Playlist Error',
                        description='❌ Could not retrieve information from the playlist entry.',
                        color=discord.Color.red()
                    )
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await ctx.send(ctx.author.mention, embed=embed)
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
                final_duration = f"{hour}:{minutes:02d}:{seconds:02d}"
            else:
                seconds = duration % (24 * 3600)
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60
                final_duration = f"{hour}:{minutes:02d}:{seconds:02d}"
            
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
                embed.add_field(name='Video Duration', value=final_duration, inline=True)
                embed.add_field(name='Likes', value=format(meta.get('like_count', 0), ',d'), inline=True)
                
                embed.add_field(name='Author', value=meta.get('uploader', 'Unknown'), inline=True)
            
            await ctx.send(ctx.author.mention, embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title='Error: Info Grab Failed',
                description=f'❌ Error retrieving video information:\n`{e}`',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)


    @commands.command()
    async def vidgrab(self, ctx, url: str):
        """Download and send a video from a given URL.

        This command downloads a video from the provided URL and sends it back to the Discord channel.
        Handles various error cases including large files and download failures.

        :param ctx: The invocation context containing command information
        :type ctx: discord.ext.commands.Context
        :param url: The URL of the video to download
        :type url: str

        :returns: None

        :raises:

            - RuntimeError: If video download fails
            - discord.HTTPException: If Discord API operations fail

        :note:

            - Videos are temporarily stored locally during processing
            - Downloaded files are automatically deleted after sending
            - Maximum file size is limited by Discord's upload limits

        :example:

            !vidgrab https://example.com/video.mp4
        """
        embed = discord.Embed(
                title='Queueing Video',
                description='Processing your video download... this may take a moment.',
                color=discord.Color.yellow()
            )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(ctx.author.mention, embed=embed)

        loop = asyncio.get_event_loop()
        video_path = await loop.run_in_executor(None, download_video, url)

        if video_path == "TOO_LARGE":
            embed = discord.Embed(
                title='Error: File Too Large',
                description='❌ The video is too large to be sent on Discord.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
        elif video_path:
            embed = discord.Embed(
                title='Succesful Video Grab',
                description='✅ Here is your video.',
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed, file=discord.File(video_path))
            os.remove(video_path)
        else:
            embed = discord.Embed(
                title='Error: Download Failed',
                description='❌ Failed to download the video.',
                color=discord.Color.red()
            )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def gifconvert(self, ctx, url: str = None):
        """
        This command accepts either a video URL or an uploaded video file and converts it
        to an animated GIF. The converted GIF is sent back to the channel.

        :param ctx: The Discord command context
        :type ctx: commands.Context
        :param url: Optional URL of the video to convert
        :type url: str
        
        :return: None
        
        :raises: 

            - RuntimeError: If video download fails
            - ValueError: If invalid file type is provided
        
        :note:

            - Supported formats: MP4, WEBM, MOV
            - Maximum file size may be limited by Discord
            - Temporary files are automatically cleaned up
        
        :example:

            -gifconvert https://example.com/video.mp4
            or
            -gifconvert (with attached video file)
        """
        allowed_gifconvert_extensions = [
            ext.lower() for ext in config.get("ALLOWED_GIFCONVERT_EXTENSIONS", [])
            ]

        if url and ctx.message.attachments:
            embed = discord.Embed(
                title='Error: Bad Input',
                description='❌ Please provide either a URL or a file upload, not both.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        video_path = None

        if url:
            embed = discord.Embed(
            title='Queuing GIF Conversion',
            description='Downloading video... please wait.',
            color=discord.Color.yellow()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            loop = asyncio.get_event_loop()
            video_path = await loop.run_in_executor(None, download_video, url)

            if video_path:
                file_extension = os.path.splitext(video_path)[1].lower()
                if file_extension not in allowed_gifconvert_extensions:
                    os.remove(video_path)
                    embed = discord.Embed(
                    title='Error: Bad File Type',
                    description='❌ Invalid video format. Only `MP4, WEBM, and MOV` are supported.',
                    color=discord.Color.red()
                    )
                    embed.set_thumbnail(url=ctx.author.display_avatar.url)
                    await ctx.send(ctx.author.mention, embed=embed)
                    return

        elif ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            file_extension = os.path.splitext(attachment.filename)[1].lower()


            if file_extension not in allowed_gifconvert_extensions:
                embed = discord.Embed(
                    title='Error: Bad File Type',
                    description='❌ Invalid video format. Only `MP4, WEBM, and MOV` are supported.',
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(ctx.author.mention, embed=embed)
                return

            embed = discord.Embed(
                title='Queuing GIF Conversion',
                description='Downloading video... please wait.',
                color=discord.Color.yellow()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            video_path = await self.download_attachment(attachment)

        else:
            embed = discord.Embed(
                title='Error: Bad Input',
                description='❌ You must provide either a URL or upload a video file.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        if not video_path:
            embed = discord.Embed(
                        title='Error: Could not Process',
                        description='❌ Failed to process the video.',
                        color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)
            return

        loop = asyncio.get_event_loop()
        gif_path = await loop.run_in_executor(None, convert_to_gif, video_path)

        if gif_path:
            embed = discord.Embed(
                title='Succesful GIF Convert',
                description='✅ Here is your GIF.',
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, file=discord.File(gif_path))
            os.remove(gif_path)
            os.remove(video_path)
        else:
            embed = discord.Embed(
                title='Error: Conversion Failed',
                description='❌ Failed to convert video to a GIF.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.send(ctx.author.mention, embed=embed)


    async def download_attachment(self, attachment):
        """
        Download a Discord attachment to the local video downloads directory.

        :param attachment: The Discord attachment object to download
        :type attachment: discord.Attachment
        :return: The full path to the downloaded file if successful, None otherwise
        :rtype: str | None

        :note:
        
            - Creates the download directory if it doesn't exist
            - Overwrites existing files with the same name
            - TODO: Make directory configurable via config.toml

        :example:
            .. code-block:: python

                file_path = await download_attachment(message.attachments[0])
                if file_path:
                    print(f"Saved to {file_path}")
        """
        video_download_dir = "vid_downloads" # TODO: Make this come from config.toml instead.
        os.makedirs(video_download_dir, exist_ok=True)

        file_path = os.path.join(video_download_dir, attachment.filename)

        try:
            await attachment.save(file_path)
            return file_path
        except:
            return None


async def setup(bot):
    await bot.add_cog(DownloadStreamCommands(bot))
