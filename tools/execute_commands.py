from utils.tools import new_tool
from utils.logger import Logger
import configparser
import colorama
import subprocess

logger = Logger('tool_execute')
conf = configparser.ConfigParser()
conf.read('config.ini')

colorama.init()

os_version = conf.get('term', 'os_version')
working_directory = conf.get('term', 'working_directory')

@new_tool('execute_commands', {
  'name': 'execute_commands',
  'description': f'Executes a list of {os_version} commands.',
  'parameters': {
    'type': 'object',
    'properties': {
      'commands': {
        'type': 'array',
        'description': 'An array of commands to execute.',
        'items': {
          'type': 'string',
          'description': 'A command to execute.',
        }
      }
    },
    'required': ['commands']
  }
})
def execute_commands(comm):
  if 'commands' not in comm: return
  commands = comm['commands']
  print(f'{colorama.Fore.RED}Terminal Assistant wants to execute the following commands:{colorama.Style.RESET_ALL}')
  for command in commands:
    print(f'  {command}')
  print('Do you want to execute these commands? (y/n)')
  answer = input('> ')
  if answer.lower() == 'y':
    responses = []
    #  execute the commands
    for command in commands:
      try:
        # Run the command and capture the output
        command = f"cd {working_directory} && {command}"
        output = subprocess.run(command, executable='/bin/bash',shell=True, capture_output=True)
        out_str = output.stdout.decode('utf-8')
        if out_str == '':
          out_str = output.stderr.decode('utf-8')
        responses.append({'role': 'system', 'content': f'{command.split(" && ")[1]}\n{out_str}'})
      except Exception as e:
        responses.append({'role': 'system', 'content': f'Failed to execute command: {command}'})
        responses.append({'role': 'system', 'content': str(e)})
    return responses
  else:
    return []