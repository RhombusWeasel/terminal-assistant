from utils.logger import Logger
from utils.tools import new_tool
from utils.async_ai import Agent
from utils.web_summary import read_page, banned_extensions
import configparser
import colorama
import requests
import time, uuid
from bs4 import BeautifulSoup
from newspaper import Article

logger = Logger('google_search')
conf = configparser.ConfigParser()
conf.read('config.ini')

colorama.init()
red = colorama.Fore.RED
grey = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
underline = "\033[4m"
reset = colorama.Style.RESET_ALL

ban_list = ' '.join([f'-site:{ext}' for ext in banned_extensions])

@new_tool('google_search_summarizer', {
  'name': 'google_search_summarizer',
  'description': 'Searches Google, summarizes the first 5 URLs found, and then summarizes the batch.',
  'parameters': {
    'type': 'object',
    'properties': {
      'query': {
        'type': 'string',
        'description': 'The search query to input to Google  Use any keywords and SEO techniques to describe what you are looking for. Don\'t include a date or year for any searches not related specifically to the past.',
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
      site_data = read_page(base_url, link, query)
      content = f"""{reset}Link: {cyan}{underline}{link}{reset}\nSummary:\n{grey}{site_data["summary"]}{reset}\n"""
      if len(site_data["links"]) > 0:
        content += "Related Links:\n"
        for l in site_data["links"]:
          content += f"{cyan}{underline}{l}{reset}\n"
      search_results.append({
        "role": 'system',
        'content': content
      })
    return search_results
  else:
    return [{'role': 'system', 'content': 'Failed to search Google.'}]

if __name__ == '__main__':
  google_search_summarizer(
    {'query': 'Pangolin information'},
    limit=5
  )