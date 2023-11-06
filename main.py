from utils.logger import Logger
from utils.async_ai import Agent
from utils.tools import tools
import configparser
import colorama
import readline
import json, time, os

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

aliases = {
  'help': {
    'description': conf.get('descriptions', 'help'),
    'aliases': conf.get('aliases', 'help').split(', ')
  },
  'tools': {
    'description': conf.get('descriptions', 'tools'),
    'aliases': conf.get('aliases', 'tools').split(', ')
  },
  'clear': {
    'description': conf.get('descriptions', 'clear'),
    'aliases': conf.get('aliases', 'clear').split(', ')
  },
  'quit': {
    'description': conf.get('descriptions', 'quit'),
    'aliases': conf.get('aliases', 'quit').split(', ')
  },
}

def load_tools():
  # Iterate the tools folder and import all tools
  files = os.listdir(os.path.join(working_directory, 'tools'))
  for file in files:
    if file.endswith('.py'):
      tool = file[:-3]
      if tool not in tools:
        __import__(f'tools.{tool}')
        logger.info(f'Loaded tool {tool}')

colorama.init()
resend = False

def reset_prompt():
  with open('prompt.json', 'r') as f:
    prompt = json.load(f)
  prompt[0]['content'].replace('{date_time}', str(time.time()))
  prompt[0]['content'].replace('{os_version}', os_version)
  prompt[0]['content'].replace('{name}', conf.get('term', 'name'))
  prompt[1]['content'].replace('{working_directory}', working_directory)
  return prompt


def process_query(query, msg, agent, resend=False):
  global funcs
  if not resend:
    msg.append({'role': 'user', 'content': query})
    print_msg(msg)
  response = agent.get_response(msg, functions=funcs, temperature=0.6)
  tokens = response['tokens']
  response = response['text']
  if 'content' in response and response['content'] != None:
    msg.append(response)
  if 'function_call' in response:
    key = response['function_call']['name']
    args = response['function_call']['arguments']
    msg.append(response)
    print_msg(msg)
    if type(args) != dict:
      try:
        args = json.loads(args)
      except:
        args = {}
    responses = tools[key]['function'](args)
    for i, response in enumerate(responses):
      msg.append(response)
      if i < len(responses) - 1:
        print_msg(msg)
      if 'resend' in response:
        msg[-1].pop('resend', None)
        # New data has been added to the message list, so we need to resend it to OpenAI with the new data
        msg = process_query(query, msg, agent, resend=True)
  token_limit = conf.getint('ai', 'token_limit')
  if tokens['total_tokens'] > token_limit:
    msg.append({'role': 'system', 'content': f'Token limit exceeded.  to conserve information please now summarize the above conversation and respond with the notes in as few tokens as possible.  Use various techniques to compress as much information into the response as possible as you will not see the information after this message.'})
    response = agent.get_response(msg, functions=funcs, temperature=0.6)
    msg = reset_prompt()
    msg.append({'role': 'user', 'content': response['text']})
  return msg

def helptext():
  print('Available commands:')
  print(f"  {colorama.Fore.YELLOW}cmd{colorama.Style.RESET_ALL} - Toggle 'Command' mode to enter commands directly.")
  col_aliases = f"{colorama.Style.RESET_ALL}, {colorama.Fore.YELLOW}"
  for alias in aliases:
    print(f'  {colorama.Fore.YELLOW}{col_aliases.join(aliases[alias]["aliases"])}{colorama.Style.RESET_ALL} - {aliases[alias]["description"]}')

def clear_screen():
  os.system('cls' if os.name=='nt' else 'clear')

def save_history():
  readline.write_history_file('history.json')

def load_history():
  try:
    readline.read_history_file('history.json')
  except FileNotFoundError:
    pass  # It's okay if the history file doesn't exist yet

def print_msg(msg):
  with open('output_full.json', 'w') as f:
    json.dump(msg, f, indent=2)
  if msg[-1]['role'] == 'assistant':
    if msg[-1]['content'] != None:
      print(f'{colorama.Fore.GREEN}Assistant:\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')
    if 'function_call' in msg[-1]:
      print(f'{colorama.Fore.YELLOW}Function call: {msg[-1]["function_call"]["name"]}{colorama.Style.RESET_ALL}')
      args = json.loads(msg[-1]['function_call']['arguments'])
      for arg in args:
        print(f'{colorama.Fore.YELLOW}  {arg}: {args[arg]}{colorama.Style.RESET_ALL}')
  elif msg[-1]['role'] == 'system':
    print(f'{colorama.Fore.CYAN}System:\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')

def main():
  global resend
  agent = Agent(name_prefix='ai')
  msg = reset_prompt()
  clear_screen()
  print(f'{colorama.Fore.CYAN}Welcome to the terminal assistant, you are running {os_version}{colorama.Style.RESET_ALL}')
  helptext()
  load_history()  # Load command history

  mode = "Query"  # The default mode is "Query"

  def recursive_complete(path, text):
    completions = []
    for root, dirs, files in os.walk(path):
      for name in dirs + files:
        full_path = os.path.join(root, name)
        if full_path.startswith(text):
          completions.append(full_path)
    return completions

  def complete_filename(text, state):
    """Tab completion function for filenames."""
    # print("Working directory:", working_directory)  # Debug print
    text = os.path.join(working_directory, text)  # Ensure text is an absolute path
    # print("Text:", text)  # Debug print
    completions = recursive_complete(working_directory, text)
    completions = [os.path.relpath(completion, working_directory) for completion in completions]  # Get relative path
    # print("Completions:", completions)  # Debug print
    try:
      return completions[state]
    except IndexError:
      return None

  readline.set_completer_delims(' ')
  readline.parse_and_bind("tab: complete")
  readline.set_completer(complete_filename)

  try:
    while True:
      p = input(f'{mode} > ')  # readline will automatically handle left/right and up/down keys
      if p in aliases['quit']['aliases']:
        break
      elif p == "cmd":  # Toggle for changing mode
        mode = "Command" if mode == "Query" else "Query"
        print(f'Switched to {mode} mode.')
        continue
      elif mode == "Command":  # In Command mode, we don't call OpenAI but use the execute_commands tool
        execute_commands_tool = tools.get('execute_commands')  # You need to make sure this tool is available
        if execute_commands_tool:
          print(f'Executing command: {p}')
          responses = execute_commands_tool['function']({'commands': [p]}, override=True)
          for response in responses:
            msg.append(response)
            print_msg(msg)
        else:
          print("Error: 'execute_commands' tool not found.")
      else:
        if p in aliases['help']['aliases']:
          helptext()
        elif p in aliases['tools']['aliases']:
          print('Available tools:')
          load_tools()
          for tool in tools:
            print(f'  {tool} - {tools[tool]["schema"]["description"]}')
        elif p in aliases['clear']['aliases']:
          msg = reset_prompt()
          clear_screen()
          print('Message history cleared')
        else:
          msg = process_query(p, msg, agent)
          print_msg(msg)
  finally:  # Save command history when the program ends
    save_history()

load_tools()
funcs = []

if __name__ == '__main__':
  funcs = [value['schema'] for key, value in tools.items()]
  main()