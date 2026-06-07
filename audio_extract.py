import ffmpeg
from demucs.pretrained import get_model
from demucs.apply import apply_model
import torchaudio
import torch


def audio_extract():
    with open("input_path.txt") as f:
        file_path = f.read().strip('"')
    ffmpeg.input(rf'{file_path}').output('output.wav', acodec='pcm_s16le').run(overwrite_output=True)


audio_extract()

device = "cuda" if torch.cuda.is_available() else "cpu"

model = get_model("htdemucs_ft")
model.to(device)
model.eval()

# Load audio with torchaudio
wav, sr = torchaudio.load("output.wav")  # shape: (channels, samples)

wav = wav.to(device)

with torch.no_grad():
    sources = apply_model(model, wav.unsqueeze(0), split=True)[0]

# sources order: drums, bass, other, vocals
vocals = sources[3].cpu()
background = sources[0].cpu() + sources[1].cpu() + sources[2].cpu()

# Save outputs
torchaudio.save("vocals.wav", vocals, sr)
torchaudio.save("background.wav", background, sr)