import os
import torch
from pydub import AudioSegment
from TTS.api import TTS

INPUT_FILE = "translated_transcript.txt"
OUTPUT_FILE = "dubbed_local.wav"
LANGUAGE = "hi"
SPEED = 1.3

def parse_transcript(filepath):
    segments = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" : ")
            if len(parts) != 3:
                continue
            start, end = parts[2].strip().split(",")
            segments.append({
                "speaker": parts[0].strip(),
                "text": parts[1].strip(),
                "start": float(start),
                "end": float(end)
            })
    return segments

def main():
    segments = parse_transcript(INPUT_FILE)
    if not segments:
        print("No segments found.")
        return

    speakers = list(set(s["speaker"] for s in segments))
    sample_map = {spk: spk + "_sample.wav" for spk in speakers}
    for spk, sample in sample_map.items():
        if not os.path.exists(sample):
            print("Missing sample: " + sample)
            return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    total_ms = int(max(s["end"] for s in segments) * 1000) + 500
    base = AudioSegment.silent(duration=total_ms)

    for i, seg in enumerate(segments):
        tmp = "tmp_" + str(i) + ".wav"
        tts.tts_to_file(
            text=seg["text"],
            speaker_wav=sample_map[seg["speaker"]],
            language=LANGUAGE,
            file_path=tmp,
            speed=SPEED
        )

        audio = AudioSegment.from_file(tmp)
        base = base.overlay(audio, position=int(seg["start"] * 1000))
        os.remove(tmp)
        print("Done: " + seg["text"][:40])

    base.export(OUTPUT_FILE, format="wav")
    print("Saved to " + OUTPUT_FILE)

main()