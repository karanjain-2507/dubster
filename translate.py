import os
import re
from groq import Groq
from langdetect import detect

INPUT_FILE = "transcript.txt"
OUTPUT_FILE = "translated_transcript.txt"

DETECT_MAP = {
    "en": "English", "hi": "Hindi", "fr": "French", "es": "Spanish",
    "de": "German", "ja": "Japanese", "ko": "Korean", "zh-cn": "Chinese",
    "ar": "Arabic", "ru": "Russian", "pt": "Portuguese", "it": "Italian",
    "tr": "Turkish", "nl": "Dutch", "pl": "Polish",
}

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

def translate_segments(segments, source_lang, target_lang, client):
    dialogue = "\n".join(
        str(i+1) + ". [" + s["speaker"] + "] (" + str(round(s["end"] - s["start"], 2)) + "s): " + s["text"]
        for i, s in enumerate(segments)
    )

    prompt = """You are a dubbing translator. Translate the dialogue from """ + source_lang + """ to """ + target_lang + """.

Each line shows the available duration in seconds. Your translation MUST perfectly fit that it can be spoken naturally within that duration. Prioritize fitting the timing over literal accuracy.

Return ONLY numbered lines in this format:
1. translated text
2. translated text

Dialogue:
""" + dialogue

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    print("Raw response: " + response.choices[0].message.content.strip()[:200])

    raw = response.choices[0].message.content.strip()
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^\d+\.\s*(?:\[.*?\]:\s*)?(.+)$", line)
        if match:
            lines.append(match.group(1).strip())

    if len(lines) != len(segments):
        print("Warning: expected " + str(len(segments)) + " lines, got " + str(len(lines)))

    return lines

def main():
    target_lang = input("Target language: ").strip()

    segments = parse_transcript(INPUT_FILE)
    if not segments:
        print("No segments found.")
        return

    combined = " ".join(s["text"] for s in segments)
    detected = detect(combined)
    source_lang = DETECT_MAP.get(detected, "English")
    print("Detected: " + source_lang)

    client = Groq(api_key='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')
    translated = translate_segments(segments, source_lang, target_lang, client)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            text = translated[i] if i < len(translated) else seg["text"]
            f.write(seg["speaker"] + " : " + text + " : " + str(seg["start"]) + "," + str(seg["end"]) + "\n")

    print("Saved to " + OUTPUT_FILE)

main()