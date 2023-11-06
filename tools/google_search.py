from utils.logger import Logger
from utils.tools import new_tool
from utils.async_ai import Agent
import configparser
import colorama
import requests
import time, uuid
from bs4 import BeautifulSoup
from newspaper import Article

logger = Logger('google_search_summarizer')
conf = configparser.ConfigParser()
conf.read('config.ini')

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
  '.link', 
  '.click'
]

ban_list = " ".join("-" + ext for ext in banned_extensions)

def extract_article(url):
  try:
    article = Article(url)
    article.download()
    article.parse()
    return article.text
  except Exception as e:
    print(f"Failed to retrieve article from {cyan}{underline}{url}. {red}Error: {str(e)}{reset}")
    return None

def get_summary(query, url):
  # Create an Agent object
  agent = Agent()

  # Get the text of the URL
  text = extract_article(url)

  if text is None:
    return None
  
  # Create a message dictionary for the chat model
  m = [
    {"role": "system", "content": "You are a summary assistant, your role is to summarize the below data and include only information relevant to the users query."},
    {"role": "user", "content": f"{query}."},
    {"role": "system", "content": f"Here is the information for you to summarize:\n\n{text}"}
  ]
  
  # Generate a new UUID for the request
  req_uuid = str(uuid.uuid4())
  # Submit the request
  agent.submit_request(m, req_uuid)

  # Wait for response to be ready (this is a very naive approach, in production code, consider a better polling/backoff strategy)
  while True:
    response = agent.check_response_status(req_uuid)
    if response is not False:
      break
    time.sleep(.5)

  return response['text']['content']

@new_tool('google_search_summarizer', {
  'name': 'google_search_summarizer',
  'description': 'Searches Google, summarizes the first 5 URLs found, and then summarizes the batch.',
  'parameters': {
    'type': 'object',
    'properties': {
      'query': {
        'type': 'string',
        'description': 'The search query to input to Google.',
      }
    },
    'required': ['query']
  }
})
def google_search_summarizer(data, limit=5):
  print(f"""{reset}Searching Google for: {cyan}{underline}{data['query']}{reset}""")
  query = data['query']
  num_results = limit
  base_url = "https://www.google.com/search"
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
  }
  params = {
    "q": query + ' ' + ban_list,
    "num": num_results
  }
  response = requests.get(base_url, params=params, headers=headers)
  search_results = []

  if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    for g in soup.find_all('div', class_='tF2Cxc'):
      link = g.find('a')['href']
      print(f"""{reset}Reading: {cyan}{underline}{link}{reset}""")
      search_results.append({
        "role": 'system',
        'content': f'{reset}Link: {cyan}{underline}{link}{reset}\nSummary:\n{grey}{get_summary(query, link)}{reset}'
      })

    return search_results
  else:
    return [{'role': 'system', 'content': 'Failed to search Google.'}]

if __name__ == '__main__':
  google_search_summarizer(
    {'query': 'Pangolin information'},
    limit=5
  )