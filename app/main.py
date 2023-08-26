from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
#pip install speechRecognition
import speech_recognition as sr
from dotenv import load_dotenv
load_dotenv()

#openai.organization = "org-PpC659Yxh5y6kPFrZEWI1tiU"
openai.api_key = os.getenv("OPENAI_API_KEY")

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


@app.get("/category")
def categorize_text(text: str):
    category = _chat_completion(text, system_prompt)

    if category != "events" and category != "notes":
        category = "unknown"

    return {"category": category}


event_system_prompt = (
    "You are an assistant. Given a text about an event, structure it with 'Event title: ', with related icon infront of 'title: ', 'location: ', 'time: ', and 'description: '. icon should always be placed after every title I tell you to structured"
)

notes_system_prompt = (
    "You are an assistant. Given a text that's a note, structure it with 'Note Title: ' with related icon infront , and 'summary: ' in dot points. icon should always be placed after of every title I tell you to structured"
)


@app.get("/structurize_text")
def categorize_text_and_summarize(text: str, category: str):
    if category.lower() == "events":
        system_prompt = event_system_prompt
    elif category.lower() == "notes":
        system_prompt = notes_system_prompt
    else:
        return {"error": "Category not supported, we don't support summarize unsupported categories."}

    structurized_text = _chat_completion(text, system_prompt)
    
    try:
        if category.lower() == "events":
            title = structurized_text.split("title:")[1].split("location:")[0].strip()
            location = structurized_text.split("location:")[1].split("time:")[0].strip()
            time = structurized_text.split("time:")[1].split("description:")[0].strip()
            description = structurized_text.split("description:")[1].strip()
            
            if not (title and location and time and description):
                raise ValueError("Incomplete data received for 'events' category")

            return {
                "structurized_text": {
                    "title": title,
                    "location": location,
                    "time": time,
                    "description": description
                }
            }
        elif category.lower() == "notes":
            title = structurized_text.split("title:")[1].split("summary:")[0].strip()
            summary = structurized_text.split("summary:")[1].strip()

            if not (title and summary):
                raise ValueError("Incomplete data received for 'notes' category")

            return {
                "structurized_text": {
                    "title": title,
                    "summary": summary
                }
            }
    except (IndexError, ValueError) as e:
        return {"error": f"Error while structuring the text @ categorize_text_and_summarize function with text: {str(e)}"}

# .wav file only
@app.post("/voice_2_text")
def voice_2_text(filename: str):
    if not filename.endswith(".wav"):
        return "error: Only.wav files are supported"
    recognizer = sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Audio could not be understood"
        except sr.RequestError:
            return "API unavailable or unresponsive"


@app.post("/voices_recording_summary")
def voices_recording_summary(text: str):
    if text.startswith("error"):
        return {"error": str}
    notes_system_prompt = (
    "You are an assistant. Given a text that's generate from recording, structure it with 'recording title: ', and 'summary: ' in dot points."
    )  
    
    structurized_text = _chat_completion(text, system_prompt)
    try:
        structurized_text = _chat_completion(text, notes_system_prompt)
        print(structurized_text)

        title = structurized_text.split("recording title:")[1].split("Summary:")[0].strip()
        summary = structurized_text.split("summary:")[1].strip()

        # Check if all fields have been extracted properly
        if not (title and summary):
            raise ValueError("Incomplete data received for 'voices recording' category")

        return {
            "structurized_text": {
                "title": title,
                "summary": summary
            }
        }
    except (IndexError, ValueError) as e:
        return {"error": f"Error while structuring the text: {str(e)}"}
    

# print('running on http://127.0.0.1:8000')