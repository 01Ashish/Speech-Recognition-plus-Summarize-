import gradio as gr
from faster_whisper import WhisperModel
from time import time
import logging
import json
import requests
import translators as ts


# Initialize logging
logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

CHOICES = [
    "tiny", "tiny.en", "base", 
    "base.en", "small", "small.en", 
    "medium", "medium.en"
]

# Function to load model
def load_model(model):
    download_path_int8 = "int8"  # Adjust path as needed for Hugging Face Spaces
    return WhisperModel(model, device="cpu", compute_type="int8", download_root=download_path_int8)

# Current model (default to small)
current_model = load_model("small")

def transcribe(audio_file, model):
    global current_model

    # Load the model if different size is selected
    if current_model.model != model:
        current_model = load_model(model)

    start = time()
    segments, info = current_model.transcribe(
        audio_file,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    # Prepare JSON output
    transcript = [ts.translate_text(segment.text) for segment in segments]
    print(f"Time Taken to transcribe: {time() - start}")
    print(transcript)
    output = transcript
    #y = json.dumps(output)    
    #x= [d["text"] for d in y["transcript"]]
    
    global p 
    p = " ".join(transcript)

    return json.dumps(output)

def summarize_text(max_length):
    headers = {"Authorization": "Bearer {TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    min_length = max_length // 4

    payload = {
        "inputs": p,
        "parameters": {"min_length": min_length, "max_length": max_length}
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    summary = response.json()
    return summary




    # Create first interface for transcribed text


    # Create second interface for summarization length
    



interface1 = gr.Interface(fn=transcribe,
                          inputs=[gr.Audio(type="filepath", label="Upload MP3 Audio File"),
                                  gr.Dropdown(choices=CHOICES, value="small", label="Model")],
                          outputs=gr.JSON(label="Transcription with Timestamps"),
                          title="Whisper Transcription Service",
                          description="Upload an MP3 audio file to transcribe. Select the model. The output includes the transcription with timestamps.",
                          concurrency_limit=2)

interface2 = gr.Interface(fn=summarize_text,
                          inputs=[gr.Slider(value=60, label="Max Length for Text Summarization", minimum=10, maximum=500)], 
                                  outputs=gr.Textbox(label="Summarized Text", type="text", value="Summary will appear here"))

lst = [x for x in dir(interface1) if '__' not in x]
# Combine them using Blocks
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            interface1.render()
        with gr.Column():
            # interface2.render()
            interface2.render()
demo.launch()
