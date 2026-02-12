import os
from dotenv import load_dotenv
from IPython.display import display, Markdown
from openai import OpenAI

from bs4 import BeautifulSoup
import requests

# standard header to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

def fetch_website_contents(url):
    """Return the title and contents of the website at the given url;
    truncate to 2000 charcters as a sensible limit

    Args:
        url (str): url of the website to scrape
    """

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"

    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()

        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = "No content found"

    return (title + "\n\n" + text)[:2000]

def fetch_website_links(url):
    """Return the links of the website at the given url;
    truncate to 2000 charcters as a sensible limit

    Args:
        url (str): url of the website to scrape
    """

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

# check api key valid or not
if not api_key:
    raise ValueError("Please set your OpenAI API key as an environment variable")
elif not api_key.startswith("sk-proj-"):
    raise ValueError("Your OpenAI API key does not appear to be valid")
elif api_key.strip() != api_key:
    raise ValueError("Your OpenAI API key appears to have leading/trailing whitespace")

openai = OpenAI()
ed_donner_website = "https://www.edwarddonner.com/"


# web scraping using openai
system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

user_propmt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.
"""

def message_for(website):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_propmt_prefix + website}
    ]

def summarize_website(website):
    website_contents = fetch_website_contents(website)
    resposne = openai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=message_for(website_contents)
    )
    return resposne.choices[0].message.content

def display_summary(url):
    summary = summarize_website(url)
    display(Markdown(summary))

if __name__ == "__main__":
    display_summary(ed_donner_website)
    