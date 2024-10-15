from utils.logger import Logger
from utils.tools import new_tool
from utils.async_ai import Agent
from utils.web_summary import read_page
import requests
import urllib
import time, uuid, json
from bs4 import BeautifulSoup
import colorama

logger = Logger('website_researcher')

colorama.init()
red = colorama.Fore.RED
grey = colorama.Fore.LIGHTBLACK_EX
cyan = colorama.Fore.CYAN
underline = "\033[4m"
reset = colorama.Style.RESET_ALL

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

    def crawl(base_url, url, depth):
        if depth > max_depth or url in visited:
            return
        visited.add(url)
        site_data = read_page(base_url, url, query)
        r_data.append({
            'url': url,
            'summary': site_data['summary'],
            'links': site_data['links']
        })
        logger.info(f"Summary for {cyan}{underline}{url}{reset}:\n{grey}{site_data['summary']}{reset}\n")

        if len(site_data['links']) > 0 and depth < max_depth:
            for link in site_data['links']:
                time.sleep(delay)
                crawl(base_url, link, depth + 1)

    crawl(base_url, base_url, 0)
    return [{"role": "system", "content": f"{json.dumps(r_data)}", "resend": True}]

if __name__ == '__main__':
    website_researcher({
        'base_url': 'https://example.com',
        'query': 'Sample research query',
        'max_depth': 2,
        'delay': 2
    })
