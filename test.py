import gradio as gr
from faster_whisper import WhisperModel
import logging
import json
import requests
import translators as ts

logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
def load_model(model):
    download_path_int8 = "int8"  # Adjust path as needed for Hugging Face Spaces
    return WhisperModel(model, device="cpu", compute_type="int8", download_root=download_path_int8)

current_model = load_model("small")
audio_file = "/home/ashishdixit/Downloads/Short Stories _ Moral Stories _ The True Friend _ writtentreasures shortstoriesinenglish.mp3"
segments, info = current_model.transcribe(
        audio_file,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

transcript = [segment.text for segment in segments]

print(transcript)

ans = []

for x in transcript:
    y = ts.translate_text(x)
    ans.append(y)

print(ans)