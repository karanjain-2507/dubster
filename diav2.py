import whisperx
from whisperx.diarize import DiarizationPipeline

device = "cuda"
audio_file = r'C:\Users\Karan Jain\Desktop\Projects\dubster\vocals.wav'
batch_size = 8
compute_type = "float16"
MERGE_GAP = 0.7

# 1. transcribe
model = whisperx.load_model("medium", device, compute_type=compute_type)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)

# 2. align
model_a, metadata = whisperx.load_align_model(
    language_code=result["language"], device=device
)
result = whisperx.align(result["segments"], model_a, metadata, audio, device)
print("Alignment done.")

# 3. diarise
diarize_model = DiarizationPipeline(
    token="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", device=device
)
diarize_segments = diarize_model(audio_file)
print("Diarisation done.")
result = whisperx.assign_word_speakers(diarize_segments, result)

# 4. merge consecutive same-speaker segments within 0.7s
segments = result["segments"]
merged = []
for seg in segments:
    speaker = seg.get("speaker", "UNKNOWN")
    text = seg["text"].strip()
    start = round(seg["start"], 2)
    end = round(seg["end"], 2)
    MAX_CHARS = 400
    if (merged and
        merged[-1]["speaker"] == speaker and
        start - merged[-1]["end"] <= MERGE_GAP and len(merged[-1]["text"]) + len(text) < MAX_CHARS):
        merged[-1]["text"] += " " + text
        merged[-1]["end"] = end
    else:
        merged.append({"speaker": speaker, "text": text, "start": start, "end": end})

# 5. write
output_file = "transcript.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for seg in merged:
        f.write(seg["speaker"] + " : " + seg["text"] + " : " + str(seg["start"]) + "," + str(seg["end"]) + "\n")

print("Saved transcript to " + output_file)
print("Segments before merge: " + str(len(segments)) + ", after: " + str(len(merged)))