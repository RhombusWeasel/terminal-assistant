from utils.logger import Logger
from utils.tools import new_tool
from utils.async_ai import Agent
import requests
import urllib
import time, uuid, json
from bs4 import BeautifulSoup
from newspaper import Article
import colorama

logger = Logger('website_researcher')

colorama.init()
red = colorama.Fore.RED
grey = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
underline = "\033[4m"
reset = colorama.Style.RESET_ALL

def extract_article(url):
    # Use BeautifulSoup to get all text from the webpage
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    }
    s = requests.Session()
    url_contents = s.get(url, headers=headers).text
    soup = BeautifulSoup(url_contents, "html", features='lxml')
    text = soup.getText()
    # print(text)
    return text

def get_summary(query, url):
    agent = Agent()
    text = extract_article(url)

    if text is None:
        return None
    # print(text)

    m = [
        {"role": "system", "content": "You are a research assistant, your role is to read the below data and determine if the data is relevant to the users query.  Respond with a full report of the page for the user with as much information as possible, if no information is relevant to the users query then respond with simply 'No relevant data.'  Your report should contain enough information for the user to not need to read the page at all, include as much data from the page as possible in as few words as possible."},
        {"role": "user", "content": f"{query}."},
        {"role": "system", "content": f"Here is the information for you to research:\n\n{text}"}
    ]

    req_uuid = str(uuid.uuid4())
    agent.submit_request(m, req_uuid)

    while True:
        response = agent.check_response_status(req_uuid)
        if response is not False:
            break
        time.sleep(.5)

    return response['text']['content']

@new_tool('website_researcher', {
    'name': 'website_researcher',
    'description': 'Performs research on a specific website by following links on the site to gather knowledge.',
    'parameters': {
        'type': 'object',
        'properties': {
            'base_url': {
                'type': 'string',
                'description': 'The base URL of the website to start the research.',
            },
            'query': {
                'type': 'string',
                'description': 'The query is not a search term more a set of instructions for the researcher agent, this should contain as much detail as possible for the researcher to provide accurate information.  If the user is vague about their requirements then add additional detail that the user omitted.',
            },
            'max_depth': {
                'type': 'integer',
                'description': 'The maximum depth to follow links from the base URL.',
                'default': 3
            },
            'delay': {
                'type': 'integer',
                'description': 'The delay in seconds between requests to avoid overwhelming the server.',
                'default': 1
            }
        },
        'required': ['base_url', 'query']
    }
})
def website_researcher(data):
    base_url = data['base_url']
    query = data['query']
    max_depth = data.get('max_depth', 3)
    delay = data.get('delay', 1)
    visited = set()
    r_data = []

    def get_links(url):
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
    
    def crawl(url, depth):
        if depth > max_depth or url in visited:
            return
        print(f"Visiting: {cyan}{underline}{url}{reset}")
        visited.add(url)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            summary = get_summary(query, url)
            r_data.append({
                'url': url,
                'info': summary
            })
            print(f"Summary for {cyan}{underline}{url}{reset}:\n{grey}{summary}{reset}\n")
            
            links = get_links(url)
            if len(links) > 0 and depth < max_depth:
                for link in links:
                    time.sleep(delay)
                    crawl(link, depth + 1)

    crawl(base_url, 0)
    return [{"role": "system", "content": f"{json.dumps(r_data)}", "resend": True}]

if __name__ == '__main__':
    website_researcher({
        'base_url': 'https://example.com',
        'query': 'Sample research query',
        'max_depth': 2,
        'delay': 2
    })
