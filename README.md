# DUBSTER
Dubs your videos into any language you want. Supports 20+ languages including Hindi, English, Spanish, French, Russian and Arabic.

# SETUP INSTRUCTIONS:-
 ## Requirements:-
   - Python 3.10
   - FFMPEG in PATH
   - CUDA enabled GPU
   - Two virtual environments (dependency conflicts between WhisperX and XTTS require separate envs)
   - HUGGINGFACE, GROQ and BOSON AI APIS

# USAGE INSTRUCTIONS:-
  - Clone the Repository
  
  - Execute the following commands in terminal
        
        python -m venv venv310
        venv310\Scripts\activate
        pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
        pip install demucs pydub langdetect groq TTS ffmpeg-python
    ---
        python -m venv venvw
        venvw\Scripts\activate
        pip install torch==2.8.0 torchaudio==2.8.0 torchvision==0.23.0 --index-url https://download.pytorch.org/whl/cu126
        pip install whisperx
        pip install pyannote.audio==4.0.4
- execute `python run.py`

# PIPELINE

```
Video → Audio extraction → Vocal separation (HTDemucs)
     → Transcription + Diarization (WhisperX + Pyannote)
     → Translation (Groq API)
     → Voice sample extraction
     → TTS with voice cloning (XTTS v2 or Boson API)
     → Merge with background → output.mp4
```

# REASONS FOR MODELS
- Vocal Seperation: HTDemucs: Best Quality, used fine tuned version so that it uses less computation power
- Transcription: WhisperX: Easy to implement. Built in Pynnote Wrapper for Diarisation
- Translation: openai/gpt-oss-120b using Groq: LLM based translation for context preservation. Wasn't able to run locally due to Hardware Constraints.
- TTS: XTTS v2 and Boson AI: Choice between 2 approaches. XTTS v2 runs locally and is free but lacks quality. Boson AI is implemented using Cloud APIs gives quality but is costly. Both support Voice Cloning

# KNOWN LIMITATIONS
- Speaker Diarisation Accuracy
- Audio Timing
- Speaker Diarisation may fail if one speaker is Dominant
- Overlapping in some places

