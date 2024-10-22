from utils.logger import Logger
from utils.async_ai import Agent
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import TerminalFormatter
from pygments import highlight
import configparser
import time, uuid, json, os, re
import colorama

logger = Logger('compress_context')
conf = configparser.ConfigParser()
conf.read('config.ini')
working_directory = conf.get('term', 'working_directory')

summary_prompt = '''
You are a summary assistant, your role is to summarize the below data and include 
only information relevant to the conversation that will be required to continue 
the conversation later.

Respond in markdown format to provide a detailed report of the following text.
The report shoould include a summary of all the questions asked by the user and
the responses given by the agent.  The report should also include any important
information that will be required to continue the conversation later.
If any system information is present such as reading/writing files, or any other
system information, please include that in the report as well.
'''

def reset_prompt():
  with open('prompt.json', 'r') as f:
    prompt = json.load(f)
  prompt[0]['content'] = prompt[0]['content'].replace('{date_time}',  str(time.strftime('%Y-%m-%d %H:%M:%S')))
  prompt[0]['content'] = prompt[0]['content'].replace('{os_version}', conf.get('term', 'os_version'))
  prompt[0]['content'] = prompt[0]['content'].replace('{name}',       conf.get('term', 'name'))
  prompt[0]['content'] = prompt[0]['content'].replace('{working_directory}', working_directory)
  prompt[0]['content'] = prompt[0]['content'].replace('{username}',   conf.get('user', 'username'))
  prompt[0]['content'] = prompt[0]['content'].replace('{location}',   conf.get('user', 'location'))
  return prompt

def highlight_code(content):
  code_pattern = r"```(\w+)(.*?)```"
  code_blocks = re.findall(code_pattern, content, re.DOTALL)
  for lang, code in code_blocks:
    if lang == '':
      lang = 'bash'
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = TerminalFormatter(style='colorful', bg='light')
    highlighted_code = highlight(code, lexer, formatter)
    content = content.replace(f"```{lang}{code}```", f"{highlighted_code}{colorama.Fore.GREEN}")

  # Add a second check for code blocks without language labels
  code_pattern = r"```(.*?)```"
  code_blocks = re.findall(code_pattern, content, re.DOTALL)
  for code in code_blocks:
    lang = 'bash'  # Assume all code blocks without language labels are bash
    lexer = get_lexer_by_name(lang, stripall=True)
    formatter = TerminalFormatter(style='colorful', bg='light')
    highlighted_code = highlight(code, lexer, formatter)
    content = content.replace(f"```{code}```", f"{highlighted_code}{colorama.Fore.GREEN}")
  return content

def print_msg(msg, filepath='output/full.json'):
  with open(filepath, 'w') as f:
    json.dump(msg, f, indent=2)
  if msg[-1]['role'] == 'assistant':
    if msg[-1]['content'] != None:
      content = msg[-1]['content']
      highlighted_content = highlight_code(content)
      # highlighted_content = new_highlight(content)
      print(f'{colorama.Fore.WHITE}{conf.get("term", "name")}{colorama.Style.RESET_ALL}:\n{colorama.Fore.GREEN}{highlighted_content}{colorama.Style.RESET_ALL}')
    if 'function_call' in msg[-1]:
      print(f'{colorama.Fore.YELLOW}Function call{colorama.Style.RESET_ALL}: {msg[-1]["function_call"]["name"]}{colorama.Style.RESET_ALL}')
      args = json.loads(msg[-1]['function_call']['arguments'])
      for arg in args:
        if arg != 'response':
          print(f'{colorama.Fore.YELLOW}  {arg}: {args[arg]}{colorama.Style.RESET_ALL}')
  elif msg[-1]['role'] == 'system':
    print(f'{colorama.Fore.CYAN}System:{colorama.Style.RESET_ALL}\n{msg[-1]["content"]}{colorama.Style.RESET_ALL}')

def compress_context(messages):
    # Messages is a list of message objects in the form {'role': 'user', 'content': 'message'}
    # The goal of this function is to compress the context by removing any unnecessary information.
    # This will be done by prompting another agent tasked with summarizing the conversation.
    agent = Agent()
    data_str = ''
    for message in messages:
        data_str += f'{message["role"]}: {message["content"]}\n'
    print(data_str)
    m = [
        {'role': 'system', 'content': summary_prompt},
        {'role': 'system', 'content': data_str}
    ]
    req_uuid = str(uuid.uuid4())
    agent.submit_request(m, req_uuid)
    while True:
        response = agent.check_response_status(req_uuid)
        if response is not False:
            break
        time.sleep(.5)
    with open('prompt.json', 'r') as f:
        prompt = json.load(f)
    prompt.append({'role': 'system', 'content': 'The context window was exceeded, below is a summary of the conversation you have been having with the user.  Continue the conversation with the user as if the context window had not been exceeded.'})
    prompt.append({'role': 'system', 'content': response['text']['content']})
    return prompt