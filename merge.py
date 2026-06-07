from pydub import AudioSegment
import subprocess

with open("input_path.txt") as f:
    VIDEO_FILE = f.read().strip('"')
DUBBED_FILE = "dubbed.wav"
BACKGROUND_FILE = "background.wav"
MIXED_FILE = "mixed.wav"
OUTPUT_FILE = "output.mp4"

# mix dubbed vocals with background
dubbed = AudioSegment.from_file(DUBBED_FILE)
background = AudioSegment.from_file(BACKGROUND_FILE)

# match lengths
if len(background) > len(dubbed):
    dubbed = dubbed + AudioSegment.silent(duration=len(background) - len(dubbed))
elif len(dubbed) > len(background):
    background = background + AudioSegment.silent(duration=len(dubbed) - len(background))

mixed = dubbed.overlay(background)
mixed.export(MIXED_FILE, format="wav")
print("Mixed audio saved to " + MIXED_FILE)

# replace audio in video
subprocess.run([
    "ffmpeg", "-y",
    "-i", VIDEO_FILE,
    "-i", MIXED_FILE,
    "-c:v", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-shortest",
    OUTPUT_FILE
])
print("Saved to " + OUTPUT_FILE)