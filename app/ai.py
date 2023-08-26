from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import json
import speech_recognition as sr
import markdown

def convert_to_markdown(text):
    return markdown.markdown(text)

chat = ChatOpenAI(temperature=0, openai_api_key="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")


def text_2_category(text:str) -> str:
  template = (
    "You are an assistant that categorizes text. If the text mentions specific dates, times, or events, you reply 'events'. If the text seems meaningful and can be summarized, even if it's a general statement or fact, you reply 'notes'. If the text appears nonsensical, repetitive, or cannot be summarized meaningfully, you reply 'unknown'."
  )
  system_message_template = SystemMessagePromptTemplate.from_template(template)
  human_template = "{text}"
  human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

  chat_template = ChatPromptTemplate.from_messages(
      [system_message_template, human_message_prompt]
  )

  formatted_prompt = chat_template.format_prompt(text=text).to_messages()
  category = chat(formatted_prompt).content
  #return json.dumps({"category": category})
  return category

def structurize_text(text: str, category: str = "unknown") -> str:
    if category.lower() == "events":
        template = (
            "You are an assistant. Given a text about an event, structure it with 'Event title: ' with related icon infront of title, 'location: ', 'Time: ', and 'Description: '."
        )
    elif category.lower() == "notes":
        template = (
            "You are an assistant. Given a text that's a note, structure it with 'Note Title: ' with related icon and 'Summary: ' in dot points."
        )
    else:
        template = (
              "Reply 'Sorry, we don't understand your content. Please retake or reupload the picture. Thank you.' with error icon at front of the text."
          )

    system_message_template = SystemMessagePromptTemplate.from_template(template)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_template = ChatPromptTemplate.from_messages(
        [system_message_template, human_message_prompt]
    )

    formatted_prompt = chat_template.format_prompt(text=text).to_messages()
    structured_text = chat(formatted_prompt).content
    if category.lower() == "events":
        temp = structured_text.split("\n")
         
        if len(temp) != 4:
            return 'error'
        return json.dumps({
            "Event Title": convert_to_markdown(temp[0].split(':')[1]),
            "Location": convert_to_markdown(temp[1].split(':')[1]),
            "Time": convert_to_markdown(temp[2].split(':')[1]),
            "Description": convert_to_markdown(temp[3].split(':')[1])
        }, ensure_ascii=False)
    elif category.lower() == "notes":
        temp = structured_text.split("\n\n")
        
        if len(temp) != 2:
            return 'error'
        
        return json.dumps({
            "Title": convert_to_markdown(temp[0].split(':')[1]),
            "Summary": convert_to_markdown(temp[1].split(':')[1])
        }, ensure_ascii=False)    
    else:
        return json.dumps({"error": convert_to_markdown(structured_text)}, ensure_ascii=False)


#voice recognition (only .wav files are supported)
def speech_to_text(audio_file: str) -> str:
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_data)
            return convert_to_markdown(text)
        except sr.UnknownValueError:
            return "Audio could not be understood"
        except sr.RequestError:
            return "API unavailable or unresponsive"

def speech_text_summary(text: str) -> str:
  template = (
    "You are an assistant that summarizes text from speech. Provide 'Title: ' for speech title, and 'summary: ' for summary of the speech."
  )
  system_message_template = SystemMessagePromptTemplate.from_template(template)
  human_template = "{text}"
  human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

  chat_template = ChatPromptTemplate.from_messages(
      [system_message_template, human_message_prompt]
  )

  formatted_prompt = chat_template.format_prompt(text=text).to_messages()
  structured_text = chat(formatted_prompt).content
  temp = structured_text.split("\n\n")
  return json.dumps({
      "Title": convert_to_markdown(temp[0].split(':')[1]),
      "Summary": convert_to_markdown(temp[1].split(':')[1])
  }, ensure_ascii=False)  



# example = "Sync, Event on September 22~23, wellcommmee to have fun with us @ Usyd"
# example2 = "Dog is so cute, they are omnivore and are the best friends with ppl."
# example3 = "Daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
# example4 = "Dace class: thursday night on 28/04/2022 asdasdasdasdsad"

# Test the function
#print(speech_to_text("../test_img/record.wav"))
#print(speech_text_summary("How are you doing? I really like your stuff"))
#print(speech_text_summary("Tiday is sunny day, i went to sydney opera house and having fun with sky diving, but tomorrow is hackthon which make it really shit day to work"))
#print(text_2_category(example5))
# print(structurize_text(example5,text_2_category(example5)))
#print(structurize_text(example,"events"))
#print(structurize_text(example2,text_2_category(example2)))
#print(structurize_text(example3,text_2_category(example3)))
# print(structurize_text(example4,text_2_category(example4)))
#print(text_2_category(example3))
