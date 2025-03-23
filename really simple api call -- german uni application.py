import os
import requests
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
import openai 

# Paste your API key here directly
api_key = ""

# Set up the OpenAI API key
openai.api_key = api_key

# Step 1: Create your prompts

system_prompt = "You are a asistant for those people who want to apply for university in german. You should be clear about the strength of each german uni and the application demand. You should provide the student the detail step for the preperation and all the important info."
user_prompt = """
    I am a chinese student now study the robotics in china and wanna go to germany for further relevant master degree. give me some uni info and tell me how to prepare?
"""

# Step 2: Make the messages list

messages = [{"role":"system", "content" : system_prompt}, {"role":"user", "content" : user_prompt}] # fill this in

# Step 3: Call OpenAI

response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)

# Step 4: print the result

print(response.choices[0].message.content)