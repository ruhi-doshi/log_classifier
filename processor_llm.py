from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq=Groq()

def classify_with_llm(log_message):
    prompt = f'''Classify the log message into one of these categories: 
    (1) Workflow Error, (2) Deprecation Warning.
    If you can't figure out a category, use "Unclassified".
    Only return the category name. No preamble. 
    Log message: {log_message}'''
    chat_completion=groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
          {
            "role": "user",
            "content": prompt
          }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    return chat_completion.choices[0].message.content
