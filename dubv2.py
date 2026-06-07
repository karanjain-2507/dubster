import os
import base64
import requests
from pydub import AudioSegment

INPUT_FILE = "translated_transcript.txt"
OUTPUT_FILE = "dubbed.wav"
API_KEY = "bai-pbozQP4OlJmepUQWfthvOB3P8olti77gK48hIqzGfa1uKcz1"

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

def load_ref_audio(path):
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    return "data:audio/wav;base64," + b64

def synthesize(text, ref_audio_b64, tmp_path):
    resp = requests.post(
        "https://api.boson.ai/v1/audio/speech",
        headers={"Authorization": "Bearer " + API_KEY},
        json={
            "model": "higgs-audio-v3-tts",
            "input": text,
            "ref_audio": ref_audio_b64,
            "response_format": "mp3"
        }
    )
    resp.raise_for_status()
    with open(tmp_path, "wb") as f:
        f.write(resp.content)

def main():
    segments = parse_transcript(INPUT_FILE)
    if not segments:
        print("No segments found.")
        return

    speakers = list(set(s["speaker"] for s in segments))
    ref_map = {}
    for spk in speakers:
        sample = spk + "_sample.wav"
        if not os.path.exists(sample):
            print("Missing sample: " + sample)
            return
        ref_map[spk] = load_ref_audio(sample)
        print("Loaded sample for " + spk)

    total_ms = int(max(s["end"] for s in segments) * 1000) + 500
    base = AudioSegment.silent(duration=total_ms)

    for i, seg in enumerate(segments):
        tmp = "tmp_" + str(i) + ".mp3"
        synthesize(seg["text"], ref_map[seg["speaker"]], tmp)

        audio = AudioSegment.from_file(tmp)
        base = base.overlay(audio, position=int(seg["start"] * 1000))
        os.remove(tmp)
        print("Done: " + seg["text"][:40])

    base.export(OUTPUT_FILE, format="wav")
    print("Saved to " + OUTPUT_FILE)

main()