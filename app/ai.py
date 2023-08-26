from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import json

# import os
# from dotenv import load_dotenv

# load_dotenv()

# openai_api_key = os.getenv('OPENAI_API_KEY')
# print(openai_api_key)

chat = ChatOpenAI(temperature=0, openai_api_key="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")


example = "Sync, Event on September 22~23, wellcommmee to have fun with us @ Usyd"
example2 = "Dog is so cute, they are omnivore and are the best friends with ppl."
example3 = "Daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
example4 = "Dace class: thursday night on 28/04/2022 asdasdasdasdsad"


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
              "Reply 'Sorry, we don't understand your content. Please retake or reupload the picture. Thank you.' with error icon at front of the text"
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
            temp[0].split(':')[0]: temp[0].split(':')[1],
            temp[1].split(':')[0]: temp[1].split(':')[1],
            temp[2].split(':')[0]: temp[2].split(':')[1],
            temp[3].split(':')[0]: temp[3].split(':')[1]
        })
    elif category.lower() == "notes":
        temp = structured_text.split("\n\n")
        
        if len(temp) != 2:
            return 'error'
        
        return json.dumps({
            temp[0].split(':')[0]: temp[0].split(':')[1],
            temp[1].split(':')[0]: temp[1].split(':')[1]
        })    
    else:
        return json.dumps({"error": structured_text})


print(structurize_text(example,text_2_category(example)))
print(structurize_text(example2,text_2_category(example2)))
print(structurize_text(example3,text_2_category(example3)))
print(structurize_text(example4,text_2_category(example4)))
