#!/usr/bin/env python3
import sys
import subprocess
import tempfile
import os
from TTS.api import TTS

def get_media_duration(path: str) -> float:
    """
    Returns duration in seconds of a media file using ffprobe.
    """
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration for {path}: {e}")
        sys.exit(1)

def format_duration(seconds: float) -> str:
    """
    Formats seconds into human-readable string.
    """
    seconds = int(round(seconds))
    mins, secs = divmod(seconds, 60)
    if mins > 0:
        return f"{mins} min{'s' if mins > 1 else ''} and {secs} second{'s' if secs != 1 else ''}"
    else:
        return f"{secs} second{'s' if secs != 1 else ''}"

def tts_to_temp_mp3(text: str) -> str:
    """
    Generates TTS mp3 file from text and returns the file path.
    """
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
              progress_bar=False, gpu=False)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()
    tts.tts_to_file(text=text, file_path=tmp_file.name)
    return tmp_file.name

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./size.py <mediafile.mp3|mp4>")
        print("  ./size.py -tts \"Your text here\"")
        sys.exit(1)

    if sys.argv[1] == "-tts":
        if len(sys.argv) < 3:
            print("Please provide text for TTS.")
            sys.exit(1)
        text = sys.argv[2]
        print("MAKING MP3 of TTS. . . .")
        mp3_path = tts_to_temp_mp3(text)
        duration = get_media_duration(mp3_path)
        print(f"Audio duration => {format_duration(duration)}")
        os.unlink(mp3_path)
    else:
        media_path = sys.argv[1]
        if not os.path.isfile(media_path):
            print(f"File not found: {media_path}")
            sys.exit(1)
        print("CHECKING DURATION. . . .")
        duration = get_media_duration(media_path)
        ext = os.path.splitext(media_path)[1].lower()
        if ext in [".mp4", ".mkv", ".avi", ".mov"]:
            print(f"Video duration => {format_duration(duration)}")
        elif ext in [".mp3", ".wav", ".aac", ".flac", ".ogg"]:
            print(f"Audio duration => {format_duration(duration)}")
        else:
            print(f"Media duration => {format_duration(duration)}")

if __name__ == "__main__":
    main()
