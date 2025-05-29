# summary_app.py

import os
import requests
import streamlit as st
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI

# Load environment variables from .env
load_dotenv(override=True)
#api_key = os.getenv('OPENAI_API_KEY')
api_key = st.secrets.get('OPENAI_API_KEY')

# Initialize OpenAI client
openai = OpenAI(api_key=api_key)

# Set up the Streamlit page
st.set_page_config(page_title="Website Summarizer", layout="centered")
st.title("🌐 Website Summarizer")
st.markdown("Enter a website URL and get a concise summary using OpenAI GPT-4o.")

# Function to fetch and clean content from a website
def fetch_website_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.title.string if soup.title else "No title found"

        # Clean the content
        for tag in soup(["script", "style", "img", "input"]):
            tag.decompose()

        body = soup.body.get_text(separator="\n", strip=True) if soup.body else "No content found"
        return title, body

    except Exception as e:
        return "Error", f"Error fetching website content: {e}"

# UI input
url_input = st.text_input("Enter a website URL:", placeholder="https://example.com")

if url_input:
    with st.spinner("Fetching website content..."):
        title, text = fetch_website_content(url_input)

    if title.startswith("Error"):
        st.error(text)
    else:
        user_prompt = (
            f"You are looking at a website titled: {title}\n\n"
            f"The contents of this website is as follows. "
            f"Please provide a short summary in markdown. "
            f"If it includes news or announcements, summarize those too.\n\n{text}"
        )

        system_prompt = (
            "You are an assistant that analyzes the contents of a website "
            "and provides a short summary, ignoring text that might be navigation related. "
            "Respond in markdown."
        )

        with st.spinner("Summarizing content with GPT-4o..."):
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

        summary = response.choices[0].message.content
        st.subheader("🔍 Summary")
        st.markdown(summary)
