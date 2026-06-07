import subprocess
import sys
import os

BASE = r"C:\Users\Karan Jain\Desktop\Projects\dubster"
VENV310 = os.path.join(BASE, "venv310", "Scripts", "python.exe")
VENVW   = os.path.join(BASE, "venvw",   "Scripts", "python.exe")

def run(python, script, label):
    print("\n" + "="*40 + "\n>> " + label + "\n" + "="*40)
    result = subprocess.run([python, os.path.join(BASE, script)], cwd=BASE)
    if result.returncode != 0:
        print("FAILED: " + label)
        sys.exit(1)

video_path = input("Video file path: ").strip()
with open(os.path.join(BASE, "input_path.txt"), "w") as f:
    f.write(video_path)

print("\nDub engine:")
print("1. XTTS (local, venv310)")
print("2. Boson API (dubv2)")
choice = input("Choose 1 or 2: ").strip()
dub_script = "dub.py" if choice == "1" else "dubv2.py"

run(VENV310, "audio_extract.py",  "Step 1: Audio extraction + vocal separation")
run(VENVW,   "diav2.py",          "Step 2: Transcription + diarization")
run(VENV310, "translate.py",      "Step 3: Translation")
run(VENV310, "voice extract.py",  "Step 4: Voice sample extraction")
run(VENV310, dub_script,          "Step 5: Dubbing")
run(VENV310, "merge.py",          "Step 6: Merge with background")

print("\nDone. Output: output.mp4")