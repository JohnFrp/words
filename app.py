from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)

PROXY_SERVICES = [
    "https://api.allorigins.win/raw?url=",
    "https://corsproxy.io/?",
    "https://cors-anywhere.herokuapp.com/",
    "https://proxy.cors.sh/",
    "https://yacdn.org/proxy/"
]

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    
    # Try direct connection first
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
    except:
        pass
    
    # Try proxy services
    for proxy in PROXY_SERVICES:
        try:
            proxy_url = proxy + requests.utils.quote(url)
            response = requests.get(proxy_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"Proxy {proxy} failed: {str(e)}")
            time.sleep(1)
    
    return None

def extract_words(html, min_length, max_length):
    soup = BeautifulSoup(html, 'html.parser')
    words = set()
    
    # Multiple extraction strategies
    for li in soup.find_all('li'):
        text = li.get_text().strip()
        if validate_word(text, min_length, max_length):
            words.add(text)
    
    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if validate_word(text, min_length, max_length):
            words.add(text)
    
    for b in soup.find_all(['b', 'strong']):
        text = b.get_text().strip()
        if validate_word(text, min_length, max_length):
            words.add(text)
            
    return list(words)

def validate_word(text, min_length, max_length):
    return (
        min_length <= len(text) <= max_length and 
        text.isupper() and 
        re.match(r'^[A-Z]+$', text)
    )

def group_words_by_length(words):
    grouped = {}
    for word in words:
        length = len(word)
        if length not in grouped:
            grouped[length] = []
        grouped[length].append(word)
    
    for length in grouped:
        grouped[length].sort()
    
    return grouped

@app.route('/')
def index():
    url = 'https://shoptips24.com/binance-word-of-the-day-answer-today/'
    min_length = 3
    max_length = 8
    error = None
    grouped_words = {}
    
    try:
        html = fetch_url(url)
        
        if html:
            words = extract_words(html, min_length, max_length)
            grouped_words = group_words_by_length(words)
        else:
            error = "Failed to fetch data (all proxies failed)"
    except Exception as e:
        error = f"Processing error: {str(e)}"

    return render_template(
        'index.html',
        grouped_words=grouped_words,
        error=error
    )

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error=error), 500

if __name__ == '__main__':
    app.run(debug=True)