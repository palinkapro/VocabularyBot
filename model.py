import numpy
import torch
from utils import apply_tts
import wave
import contextlib
from bot_token import local_file


torch.set_grad_enabled(False)

device = torch.device('cpu')
  
symbols = '_~абвгдеёжзийклмнопрстуфхцчшщъыьэюя +.,!?…:;–'
sample_rate = 16000


def get_audio(batch):
    model = torch.jit.load(local_file,
                       map_location=device)
    model.eval()
    model = model.to(device)
    
    audio = apply_tts(texts=batch,
                        model=model,
                        sample_rate=sample_rate,
                        symbols=symbols,
                        device=device)
    return audio

def save_audio(audio, batch, folder):
    for i, _audio in enumerate(audio):
            write_wave(path=f'{folder}/{batch[i].replace("+", "")}.ogg',
            audio=(audio[i] * 32767).numpy().astype('int16'),
            sample_rate=16000)

def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)
