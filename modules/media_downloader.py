import os
import yt_dlp
import toml
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
from moviepy.video.io.VideoFileClip import VideoFileClip
import ffmpeg 
config = toml.load("config.toml")



def download_video(url):
    """Downloads a video from YouTube or Twitter."""
    VIDEO_DOWNLOAD_DIR = config["VIDEO_DOWNLOAD_DIR"]
    output_path = os.path.join(VIDEO_DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")

    if os.path.exists(filename):
        return filename
    else:
        print("Download completed, but file not found:", filename)
        return None  # Prevent returning an invalid path

def compress_video(filepath):
    """Compress the video to be under 4MB."""
    MAX_FILE_SIZE_MB = int(config["MAX_FILE_SIZE_MB"])
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    output_path = filepath.replace(".mp4", "_compressed.mp4")

    try:
        clip = VideoFileClip(filepath)
        bitrate = "300k"

        clip.write_videofile(
            output_path,
            bitrate=bitrate,
            threads=4,
            codec="libx264",
            preset="ultrafast",
            audio_codec="aac",
        )

        if os.path.getsize(output_path) > MAX_FILE_SIZE_BYTES:
            os.remove(output_path)
            return "TOO_LARGE"

        return output_path
    except Exception as e:
        print(f"Error compressing video: {e}")
        return None   

def convert_to_gif(video_path):
    """Converts a video to a GIF using FFmpeg and returns the GIF path."""
    GIF_DIR = config["GIF_DIR"]
    os.makedirs(GIF_DIR, exist_ok=True)
    gif_path = os.path.join(GIF_DIR, os.path.basename(video_path).replace(os.path.splitext(video_path)[1], ".gif"))
    try:
        print(f"Converting {video_path} to GIF...")
        # Create ffmpeg input and output objects
        input_stream = ffmpeg.input(video_path, t=10)
        output_stream = ffmpeg.output(
            input_stream, 
            gif_path, 
            vf="fps=10,scale=320:-1:flags=lanczos", 
            loop=0
        )
        # Run the ffmpeg command
        ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
        
        if os.path.exists(gif_path):
            print(f"GIF successfully created: {gif_path}")
            return gif_path
        else:
            print("GIF conversion completed, but file not found.")
            return None
    except ffmpeg.Error as e:
        print(f"Error converting to GIF: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
        return None