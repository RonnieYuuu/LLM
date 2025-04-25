import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key="")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    def __init__(self, url):
        """
        使用 Selenium 模拟浏览器访问网站，提取网页标题和正文文本
        """
        self.url = url

        # 设置无头浏览器选项
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument(f"user-agent={headers['User-Agent']}")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # 初始化 WebDriver
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)  # 等待页面加载完成（可根据网络调整时间）

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        # 提取标题和正文
        self.title = soup.title.string.strip() if soup.title else "No title found"
        for irrelevant in soup(["script", "style", "img", "input", "nav", "footer", "aside"]):
            irrelevant.decompose()
        body = soup.find("body")
        self.text = body.get_text(separator="\n", strip=True) if body else ""

def user_prompt_for(website):
    return (
        f"You are looking at a website titled {website.title}.\n"
        "The contents of this website is as follows; please provide a short summary "
        "of this website in markdown. If it includes news or announcements, summarize those too.\n\n"
        f"{website.text}"
    )

def messages_for(website):
    return [
        {"role": "system", "content": (
            "You are an assistant that analyzes the contents of a website "
            "and provides a short summary, ignoring text that might be navigation related. "
            "Respond in markdown."
        )},
        {"role": "user", "content": user_prompt_for(website)}
    ]

def summarize(url):
    website = Website(url)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_for(website)
    )
    return response.choices[0].message.content

def display_summary(url):
    summary = summarize(url)
    print(summary)

if __name__ == "__main__":
    test_url = "https://www.nytimes.com/2025/03/23/business/media/sesame-street-layoffs-funding-cuts.html"
    display_summary(test_url)
