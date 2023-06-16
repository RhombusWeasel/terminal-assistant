from utils.logger import Logger
from utils.async_ai import Agent
from utils.tools import tools
import configparser
import colorama
import readline
import json, os

logger = Logger('term')
# Get the location of the current file and set it as working directory
working_directory = os.path.dirname(os.path.abspath(__file__))
conf = configparser.ConfigParser()
conf.read('config.ini')

os_version = conf.get('term', 'os_version')
if conf.get('term', 'working_directory') != working_directory + '/':
  conf.set('term', 'working_directory', working_directory)
  with open('config.ini', 'w') as f:
    conf.write(f)

def load_tools():
  # Iterate the tools folder and import all tools
  files = os.listdir(os.path.join(working_directory, 'tools'))
  for file in files:
    if file.endswith('.py'):
      tool = file[:-3]
      if tool not in tools:
        logger.info(f'Loading tool {tool}')
        __import__(f'tools.{tool}')

colorama.init()
resend = False

def reset_prompt():
  with open('prompt.json', 'r') as f:
    prompt = json.load(f)
  return prompt

def process_query(query, msg, agent):
  global funcs
  msg.append({'role': 'user', 'content': query})
  response = agent.get_response(msg, functions=funcs)
  if 'content' in response and response['content'] != None:
    msg.append(response)
  elif 'function_call' in response:
    key = response['function_call']['name']
    args = response['function_call']['arguments']
    if type(args) != dict:
      try:
        args = json.loads(args)
      except:
        args = {}
    responses = tools[key]['function'](args)
    for response in responses:
      msg.append(response)
  return msg

aliases = {
  'help': {
    'description': conf.get('descriptions', 'help'),
    'aliases': conf.get('aliases', 'help').split(',')
  },
  'tools': {
    'description': conf.get('descriptions', 'tools'),
    'aliases': conf.get('aliases', 'tools').split(',')
  },
  'clear': {
    'description': conf.get('descriptions', 'clear'),
    'aliases': conf.get('aliases', 'clear').split(',')
  },
  'quit': {
    'description': conf.get('descriptions', 'quit'),
    'aliases': conf.get('aliases', 'quit').split(',')
  },
}

def helptext():
  print('Available commands:')
  col_aliases = f"{colorama.Style.RESET_ALL}, {colorama.Fore.YELLOW}"
  for alias in aliases:
    print(f'  {colorama.Fore.YELLOW}{col_aliases.join(aliases[alias]["aliases"])}{colorama.Style.RESET_ALL} - {aliases[alias]["description"]}')

def cls():
  os.system('cls' if os.name=='nt' else 'clear')

def save_history():
  readline.write_history_file('history.json')

def load_history():
  try:
    readline.read_history_file('history.json')
  except FileNotFoundError:
    pass  # It's okay if the history file doesn't exist yet

def main():
  global resend
  agent = Agent(name_prefix='ai')
  msg = reset_prompt()
  cls()
  print(f'{colorama.Fore.CYAN}Welcome to the terminal assistant, you are running {os_version}{colorama.Style.RESET_ALL}')
  load_history()  # Load command history
  try:
    while True:
      helptext()
      p = input('Query > ')  # readline will automatically handle left/right and up/down keys
      if p in aliases['quit']['aliases']:
        break
      elif p in aliases['help']['aliases']:
        print(helptext)
      elif p in aliases['tools']['aliases']:
        print('Available tools:')
        load_tools()
        for tool in tools:
            print(f'  {tool} - {tools[tool]["schema"]["description"]}')
      elif p in aliases['clear']['aliases']:
        msg = reset_prompt()
        cls()
        print('Message history cleared')
      else:
        msg = process_query(p, msg, agent)

      if msg[-1]['role'] == 'assistant':
        print(f'{colorama.Fore.GREEN}Assistant:\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')
      elif msg[-1]['role'] == 'system':
        print(f'{colorama.Fore.CYAN}System:\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')
      elif msg[-1]['role'] == 'user':
        print(f'{colorama.Fore.WHITE}User:\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')
  finally:  # Save command history when the program ends
    save_history()

load_tools()
funcs = []

if __name__ == '__main__':
  funcs = [value['schema'] for key, value in tools.items()]
  main()