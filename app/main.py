from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.organization = "org-PpC659Yxh5y6kPFrZEWI1tiU"
openai.api_key = "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"

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

system_prompt = (
    "You are an assistant that categorizes text. If the text mentions specific dates, times, or events, you reply "
    "'events'. If the text seems meaningful and can be summarized, even if it's a general statement or fact, "
    "you reply 'notes'. If the text appears nonsensical, repetitive, or cannot be summarized meaningfully, "
    "you reply 'unknown'."
)


def _chat_completion(text: str, system_prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.2,
    )
    return response['choices'][0]['message']['content'].lower()


@app.get("/")
def read_root():
    return {"Hello": "World after deployment"}


@app.post("/category")
def categorize_text(text: str):
    category = _chat_completion(text, system_prompt)

    if category != "events" and category != "notes":
        category = "unknown"

    return {"category": category}


event_system_prompt = (
    "You are an assistant. Given a text about an event, structure it with 'Event title: ' with related icon "
    "infront of title, 'location: ', 'Time: ', and 'Description: '."
)

notes_system_prompt = (
    "You are an assistant. Given a text that's a note, structure it with 'Note Title: ' with related icon and "
    "'Summary: ' in dot points."
)


@app.post("/structurize_text")
def categorize_text_and_summarize(text: str, category: str):
    if category.lower() == "events":
        system_prompt = event_system_prompt
    elif category.lower() == "notes":
        system_prompt = notes_system_prompt
    else:
        return {"error": "Category not supported"}

    structurized_text = _chat_completion(text, system_prompt)
    return {"structurized_text": structurized_text}

# # .wav file only
# @app.post("/voice_2_text")
# def voice_2_text(path: str):
#     if path.endswith(".wav"):
#         return speech_to_text(path)  # ai.py function
#     return {"error": "File type not supported"}
#
#
# @app.post("/voices_recording_summary")
# def voices_recording_summary(text: str):
#     return speech_text_summary(text)  # ai.py function

# print('running on http://127.0.0.1:8000')
