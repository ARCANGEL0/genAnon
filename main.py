import subprocess
import tempfile
import sys
from TTS.api import TTS



def generate_speech(prompt: str, out_path: str):
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
    tts.tts_to_file(text=prompt,language="en", speaker_wav="voice.wav", file_path=out_path)


def apply_deep_robotic_filter(input_wav: str, output_wav: str):
    """
    Creates a deep, robotic, distorted bass voice with aggressive effects.
    """
    ffmpeg_filter = (
        "asetrate=44100*0.55,"          # lower pitch (deeper)
        "aresample=44100,"              # resample to normal rate
        "atempo=0.8,"                  # slow down tempo slightly
        "bass=g=15:f=80:w=1.0,"        # strong bass boost
        "acrusher=level_in=1:level_out=1:bits=6:mode=log:aa=1,"  # heavy bitcrusher distortion
        "tremolo=f=12:d=0.8,"          # faster, deeper tremolo for robotic effect
        "chorus=0.7:0.9:55:0.4:0.25:2," # subtle chorus for eerie modulation
        "dynaudnorm=f=200"             # dynamic audio normalization for punch
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_wav,
        "-af", ffmpeg_filter,
        output_wav
    ], check=True)

def mix_with_background(speech_wav: str, bg_path: str, out_mix: str):
    """
    Mixes the processed speech with a looping, very‐low‐level
    background track.
    """
    filter_complex = (
        "[1]volume=0.015,aloop=loop=-1:size=2147483647[b];"
        "[0][b]amix=inputs=2:duration=first:dropout_transition=3"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", speech_wav,
        "-i", bg_path,
        "-filter_complex", filter_complex,
        "-c:a", "aac", "-b:a", "192k",
        out_mix
    ], check=True)

def overlay_audio_on_video(video_in: str, audio_in: str, video_out: str):
    """
    Strips original audio, then muxes in our mixed track.
    """
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_in,
        "-i", audio_in,
        "-c:v", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        video_out
    ], check=True)

def main():
    if len(sys.argv) != 4:
        print("Usage: python inject_audio.py  video.mp4  background.mp3  \"Your prompt here\"")
        sys.exit(1)

    video_path = sys.argv[1]
    background_path = sys.argv[2]
    prompt = sys.argv[3]

    with tempfile.TemporaryDirectory() as td:
        raw_speech = f"{td}/raw_speech.wav"
        deep_robotic = f"{td}/speech_deep_robotic.wav"
        mixed      = f"{td}/speech_plus_bg.aac"
        output     = "output_with_ai_voice.mp4"

        print("[1/4] Generating TTS…")
        generate_speech(prompt, raw_speech)

        print("[2/4] Applying deep robotic filter…")
        apply_deep_robotic_filter(raw_speech, deep_robotic)

        print("[3/4] Mixing in background…")
        mix_with_background(deep_robotic, background_path, mixed)

        print("[4/4] Overlaying on video…")
        overlay_audio_on_video(video_path, mixed, output)

        print("Done →", output)

if __name__ == "__main__":
    main()
