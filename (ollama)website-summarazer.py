import requests
from bs4 import BeautifulSoup

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

system_prompt = "You are an assistant that analyzes the contents of a website \
                and provides a short summary, ignoring text that might be navigation related. \
                Respond in markdown."

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled '{website.title}'."
    user_prompt += "\nThe contents of this website are as follows. \
                    Please provide a short summary of this website in markdown. \
                    If it includes news or announcements, summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summary(url):
    website = Website(url)
    payload = {
        "model": MODEL,
        "messages": messages_for(website),
        "stream": False
    }
    response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
    return print(response.json())  # This will print the summarized response

summary("https://de.wikipedia.org/wiki/Ludwig-Maximilians-Universit%C3%A4t_M%C3%BCnchen")
