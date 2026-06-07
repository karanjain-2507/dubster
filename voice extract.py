from pydub import AudioSegment

VOCALS_FILE = "vocals.wav"
TRANSCRIPT_FILE = "transcript.txt"
SAMPLE_DURATION_MS = 6000

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
                "start": float(start),
                "end": float(end)
            })
    return segments

def main():
    segments = parse_transcript(TRANSCRIPT_FILE)
    vocals = AudioSegment.from_file(VOCALS_FILE)

    # find longest segment per speaker
    best = {}
    for seg in segments:
        duration = seg["end"] - seg["start"]
        if seg["speaker"] not in best or duration > best[seg["speaker"]]["duration"]:
            best[seg["speaker"]] = {
                "start": seg["start"],
                "end": seg["end"],
                "duration": duration
            }

    for speaker, seg in best.items():
        start_ms = int(seg["start"] * 1000)
        end_ms = min(start_ms + SAMPLE_DURATION_MS, int(seg["end"] * 1000))
        clip = vocals[start_ms:end_ms]
        outfile = speaker + "_sample.wav"
        clip.export(outfile, format="wav")
        print("Saved " + outfile + " (" + str(round((end_ms - start_ms) / 1000, 2)) + "s)")

main()