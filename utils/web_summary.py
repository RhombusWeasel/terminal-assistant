import requests
from bs4 import BeautifulSoup
import time
import uuid
import json
from utils.async_ai import Agent
from utils.logger import Logger
import colorama

logger = Logger('page_reader')

colorama.init()
red = colorama.Fore.RED
grey = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
underline = "\033[4m"
reset = colorama.Style.RESET_ALL

banned_extensions = [
  '.gov', 
  '.tv',
  '.cn', 
  '.ru', 
  '.hk', 
  '.info', 
  '.cc', 
  '.pw', 
  '.tk', 
  '.xyz',
  '.site',
  '.xxx',
  '.link', 
  '.click'
]

def extract_article(url):
    # Use BeautifulSoup to get all text from the webpage
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    s = requests.Session()
    url_contents = s.get(url, headers=headers).text
    soup = BeautifulSoup(url_contents, "html.parser")
    text = soup.getText()
    logger.debug(f'Extracted text: {text}')
    return text

def get_summary(url, query):
    agent = Agent()
    text = extract_article(url)

    if text is None:
        return None
    
    m = [
        {"role": "system", "content": "You are a summary assistant, your role is to summarize the below data and include only information relevant to the users query."},
        {"role": "user", "content": f"{query}."},
        {"role": "system", "content": f"Here is the information for you to summarize:\n\n{text}"}
    ]
    
    req_uuid = str(uuid.uuid4())
    agent.submit_request(m, req_uuid)

    while True:
        response = agent.check_response_status(req_uuid)
        if response is not False:
            break
        time.sleep(.5)

    logger.debug(f'Summary: {response["text"]["content"]}')
    return response['text']['content']

def get_links(base_url, url, query):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for link in soup.find_all('a', href=True):
            next_url = link['href']
            if next_url.startswith('/'):
                next_url = base_url + next_url
            if base_url in next_url:
                links.append(next_url)
        agent = Agent()
        m = [
            {"role": "system", "content": "You role is to check the below list of links and return a list of only the most relevant links to the user's query. Fewer links are preferred in the response, the response must be parsable by pythons json.loads and should not be wrapped in a code block."},
            {"role": "user", "content": f"{query}."},
            {"role": "system", "content": f"Here is the information for you to filter:\n\n{links}"}
        ]
        req_uuid = str(uuid.uuid4())
        agent.submit_request(m, req_uuid)
        while True:
            response = agent.check_response_status(req_uuid)
            if response is not False:
                break
            time.sleep(.5)
        links = json.loads(response['text']['content'])
        return links
    return []

def read_page(base_url, url, query):
    ext = url.split('.')[-1]
    if ext in banned_extensions:
        logger.warn(f'Skipping {url} because it has a banned extension [{ext}]')
        return {
            "summary": f'Skipping {url} because it has a banned extension [{ext}]',
            "links": []
        }
    logger.info(f"Visiting: {cyan}{underline}{url}{reset}")
    return {
      "summary": get_summary(url, query),
      "links":   get_links(base_url, url, query)
    }
