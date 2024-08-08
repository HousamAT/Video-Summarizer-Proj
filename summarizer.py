import os
import shutil
from pytube import YouTube

#these libraries for downloading the mp3 file 
from pytubefix import YouTube
from pytubefix.cli import on_progress


#given a directory list all the mp3 files in that directory
def find_audio_files(path, extension=".mp3"):
    """Recursively find all files with extension in path."""
    audio_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                audio_files.append(os.path.join(root, f))

    return audio_files


def youtube_to_mp3(youtube_url: str, output_dir: str) -> str:
    """Download the audio from a youtube video, save it to output_dir as an .mp3 file.

    Returns the filename of the savied video.
    """


    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yt = YouTube(youtube_url, on_progress_callback = on_progress)
    
    ys = yt.streams.get_highest_resolution()
    ys.download(mp3=True,output_path=output_dir)

    audio_filename = find_audio_files(output_dir)[0]
    return audio_filename

def summarize_youtube_video(youtube_url, outputs_dir):
    raw_audio_dir = f"{outputs_dir}/raw_audio/"
    chunks_dir = f"{outputs_dir}/chunks"
    transcripts_file = f"{outputs_dir}/transcripts.txt"
    summary_file = f"{outputs_dir}/summary.txt"
    segment_length = 2 * 60  # chunk to 10 minute segments

    if os.path.exists(outputs_dir):
        # delete the outputs_dir folder and start from scratch
        shutil.rmtree(outputs_dir)
        os.mkdir(outputs_dir)

    # download the video using youtube-dl
    audio_filename = youtube_to_mp3(youtube_url, output_dir=raw_audio_dir)