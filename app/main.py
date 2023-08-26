from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai import *
from fastapi import Body
from typing import Dict
from pydantic import BaseModel

app = FastAPI()

# Set all origins to be allowed (wildcard)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World after deployment"}


@app.post("/category")
def categorize_text(data: str):
    return text_2_category(data)  # ai.py function

@app.post("/structurize_text")
def categorize_text_and_summarize(data: str, category:str):
    return structurize_text(data, category)  # ai.py function

# .wav file only
@app.post("/voice_2_text")
def voice_2_text(path:str):
    if path.endswith(".wav"):
        return speech_to_text(path) # ai.py function
    return {"error": "File type not supported"}

@app.post("/voices_recording_summary")
def voices_recording_summary(text: str):
    return speech_text_summary(text) # ai.py function




# print('running on http://127.0.0.1:8000')
