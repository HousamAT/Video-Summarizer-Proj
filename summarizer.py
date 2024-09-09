import os
import shutil
from pytube import YouTube
from groq import Groq #for the ai
import librosa
import soundfile as sf

import whisper

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

def chunk_audio(filename, segment_length: int, output_dir):
    """segment lenght is in seconds"""

    print(f"Chunking audio to {segment_length} second segments...")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # load audio file
    audio, sr = librosa.load(path=filename, sr=44100)

    # calculate duration in seconds
      
    duration = librosa.get_duration(y=audio, sr=sr)

    # calculate number of segments
    num_segments = int(duration / segment_length) + 1

    print(f"Chunking {num_segments} chunks...")

    # iterate through segments and save them
    for i in range(num_segments):
        start = i * segment_length * sr
        end = (i + 1) * segment_length * sr
        segment = audio[start:end]
        sf.write(os.path.join(output_dir, f"segment_{i}.mp3"), segment, sr)

    chunked_audio_files = find_audio_files(output_dir)
    return sorted(chunked_audio_files)

def transcribe_audio(audio_files: list, output_file=None, model="tiny.en") -> list:

    print("converting audio to text...")

    # Load the whisper model
    model = whisper.load_model(model)

    transcripts = []
    for audio_file in audio_files:
        # Transcribe the audio file
        result = model.transcribe(audio_file)
        transcripts.append(result["text"])

    if output_file is not None:
        # Save all transcripts to a .txt file
        with open(output_file, "w") as file:
            for transcript in transcripts:
                file.write(transcript + "\n")

    return transcripts

def summarize(
    chunks: list[str], system_prompt: str, model="gpt-3.5-turbo", output_file=None
):
    api_key = "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" #my api key from groq
    client = Groq(api_key=api_key)
    
    summaries = []

    for chunk in chunks:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Access the summary content from the response object
        summary = "".join([choice.message.content for choice in response.choices])
        summaries.append(summary)

    if output_file is not None:
        with open(output_file, "w") as file:
            for summary in summaries:
                file.write(summary + "\n")

    return summaries



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
    
    # chunk each audio file to shorter audio files (not necessary for shorter videos...)
    chunked_audio_files = chunk_audio(
        audio_filename, segment_length=segment_length, output_dir=chunks_dir
    )
    
    # transcribe each chunked audio file using whisper speech2text
    transcriptions = transcribe_audio(chunked_audio_files, transcripts_file)
    
    # summarize each transcription using chatGPT
    system_prompt = """
    You are a helpful assistant that summarizes youtube videos.
    You are provided chunks of raw audio that were transcribed from the video's audio.
    Summarize the current chunk to succint and clear bullet points of its contents.
    """
    summaries = summarize(
        transcriptions, system_prompt=system_prompt, output_file=summary_file
    )

    system_prompt_tldr = """
    You are a helpful assistant that summarizes youtube videos.
    Someone has already summarized the video to key points.
    Summarize the key points to one or two sentences that capture the essence of the video.
    """
    # put the entire summary to a single entry
    long_summary = "\n".join(summaries)
    short_summary = summarize(
        [long_summary], system_prompt=system_prompt_tldr, output_file=summary_file
    )[0]

    return long_summary, short_summary
    

#test link
#https://www.youtube.com/watch?v=g1pb2aK2we4&t=58s