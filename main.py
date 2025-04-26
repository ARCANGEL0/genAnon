import subprocess
import tempfile
import sys
from TTS.api import TTS

def generate_speech(prompt: str, out_path: str):
    """
    Uses Coqui TTS to render `prompt` to a WAV file.
    """
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC",
              progress_bar=False, gpu=False)
    tts.tts_to_file(text=prompt, file_path=out_path)

def apply_robotic_filter(input_wav: str, output_wav: str):
    """
    Lowers pitch, speeds up to compensate, adds tremolo for a robotic
    timbre.
    """
    # asetrate=lower sample rate for pitch ↓,
    # atempo=compensate duration,
    # tremolo adds amplitude modulation
    ffmpeg_filter = (
        "asetrate=44100*0.75,"
        "aresample=44100,"
        "atempo=1.3333,"
        "tremolo=f=5:d=0.8"
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
    # volume of bg set to 5%, loop indefinitely, mix so final
    # duration = speech duration
    filter_complex = (
        "[1]volume=0.05,aloop=loop=-1:size=2e+10[b];"
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

    # create temp files
    with tempfile.TemporaryDirectory() as td:
        raw_speech = f"{td}/raw_speech.wav"
        robotic    = f"{td}/speech_robotic.wav"
        mixed      = f"{td}/speech_plus_bg.aac"
        output     = "output_with_ai_voice.mp4"

        print("[1/4] Generating TTS…")
        generate_speech(prompt, raw_speech)

        print("[2/4] Applying robotic filter…")
        apply_robotic_filter(raw_speech, robotic)

        print("[3/4] Mixing in background…")
        mix_with_background(robotic, background_path, mixed)

        print("[4/4] Overlaying on video…")
        overlay_audio_on_video(video_path, mixed, output)

        print("Done →", output)

if __name__ == "__main__":
    main()
