import os
import shutil
from pytube import YouTube
from groq import Groq  # For AI summarization
import librosa
import soundfile as sf
import whisper
from pytubefix import YouTube
from pytubefix.cli import on_progress

def find_audio_files(path, extension=".mp3"):
    """Recursively find all audio files with the specified extension in the given directory.

    Args:
        path (str): The directory path to search for audio files.
        extension (str): The file extension to look for (default is ".mp3").

    Returns:
        list: A list of paths to the found audio files.
    """
    audio_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                audio_files.append(os.path.join(root, f))

    return audio_files

def youtube_to_mp3(youtube_url: str, output_dir: str) -> str:
    """Download audio from a YouTube video and save it as an .mp3 file in the specified output directory.

    Args:
        youtube_url (str): The URL of the YouTube video to download.
        output_dir (str): The directory where the .mp3 file will be saved.

    Returns:
        str: The filename of the saved audio file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    yt = YouTube(youtube_url, on_progress_callback=on_progress)
    ys = yt.streams.get_highest_resolution()
    ys.download(mp3=True, output_path=output_dir)

    audio_filename = find_audio_files(output_dir)[0]
    return audio_filename

def chunk_audio(filename, segment_length: int, output_dir):
    """Split an audio file into smaller segments of a specified length.

    Args:
        filename (str): The path to the audio file to be chunked.
        segment_length (int): The length of each segment in seconds.
        output_dir (str): The directory where the chunked audio files will be saved.

    Returns:
        list: A sorted list of paths to the chunked audio files.
    """
    print(f"Chunking audio to {segment_length} second segments...")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Load audio file
    audio, sr = librosa.load(path=filename, sr=44100)

    # Calculate duration in seconds
    duration = librosa.get_duration(y=audio, sr=sr)

    # Calculate number of segments
    num_segments = int(duration / segment_length) + 1

    print(f"Chunking {num_segments} chunks...")

    # Iterate through segments and save them
    for i in range(num_segments):
        start = i * segment_length * sr
        end = (i + 1) * segment_length * sr
        segment = audio[start:end]
        sf.write(os.path.join(output_dir, f"segment_{i}.mp3"), segment, sr)

    chunked_audio_files = find_audio_files(output_dir)
    return sorted(chunked_audio_files)

def transcribe_audio(audio_files: list, output_file=None, model="tiny.en") -> list:
    """Transcribe a list of audio files to text using the Whisper model.

    Args:
        audio_files (list): A list of paths to audio files to transcribe.
        output_file (str, optional): Path to save the transcriptions (default is None).
        model (str): The Whisper model to use for transcription (default is "tiny.en").

    Returns:
        list: A list of transcribed texts.
    """
    print("Converting audio to text...")

    # Load the Whisper model
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

def summarize(chunks: list[str], system_prompt: str, model="gpt-3.5-turbo", output_file=None):
    """Summarize a list of text chunks using the specified AI model.

    Args:
        chunks (list[str]): The list of text chunks to summarize.
        system_prompt (str): The system prompt to guide the summarization.
        model (str): The AI model to use for summarization (default is "gpt-3.5-turbo").
        output_file (str, optional): Path to save the summaries (default is None).

    Returns:
        list: A list of summaries generated for each chunk.
    """
    api_key = "Replace_With_Your_Own_API_Key"  # Get API key from Groq
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
    """Download, transcribe, and summarize a YouTube video.

    Args:
        youtube_url (str): The URL of the YouTube video to summarize.
        outputs_dir (str): The directory where output files will be saved.

    Returns:
        tuple: A tuple containing the long summary and the short summary of the video.
    """
    raw_audio_dir = f"{outputs_dir}/raw_audio/"
    chunks_dir = f"{outputs_dir}/chunks"
    transcripts_file = f"{outputs_dir}/transcripts.txt"
    summary_file = f"{outputs_dir}/summary.txt"
    segment_length = 2 * 60  # Chunk to 10-minute segments

    if os.path.exists(outputs_dir):
        # Delete the outputs_dir folder and start from scratch
        shutil.rmtree(outputs_dir)
        os.mkdir(outputs_dir)

    # Download the video using youtube-dl
    audio_filename = youtube_to_mp3(youtube_url, output_dir=raw_audio_dir)
    
    # Chunk each audio file to shorter audio files (not necessary for shorter videos...)
    chunked_audio_files = chunk_audio(
        audio_filename, segment_length=segment_length, output_dir=chunks_dir
    )
    
    # Transcribe each chunked audio file using Whisper speech-to-text
    transcriptions = transcribe_audio(chunked_audio_files, transcripts_file)
    
    # Summarize each transcription using chatGPT
    system_prompt = """
    You are a helpful assistant that summarizes YouTube videos.
    You are provided chunks of raw audio that were transcribed from the video's audio.
    Summarize the current chunk to succinct and clear bullet points of its contents.
    """
    summaries = summarize(
        transcriptions, system_prompt=system_prompt, output_file=summary_file
    )

    system_prompt_tldr = """
    You are a helpful assistant that summarizes YouTube videos.
    Someone has already summarized the video to key points.
    Summarize the key points to one or two sentences that capture the essence of the video.
    """
    # Put the entire summary into a single entry
    long_summary = "\n".join(summaries)
    short_summary = summarize(
        [long_summary], system_prompt=system_prompt_tldr, output_file=summary_file
    )[0]

    return long_summary, short_summary
    

# Test link
# https://www.youtube.com/watch?v=g1pb2aK2we4&t=58s
