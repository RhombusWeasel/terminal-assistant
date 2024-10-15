from utils.tools import new_tool
from utils.logger import Logger
from utils.prompt_tools import print_msg
import configparser
import os

logger = Logger('tool_read')
conf = configparser.ConfigParser()
conf.read('config.ini')

@new_tool('read_file', {
    'name': 'read_file',
    'description': 'Reads a file.',
    'parameters': {
      'type': 'object',
      'properties': {
        'file': {
          'type': 'string',
          'description': 'The path to the file to read. the filepath will have the current working directory added for you, simply give a path relative to the working directory.',
        }
      },
      'required': ['file']
    }
  }
)
def read_file(file):
  working_directory = conf.get('term', 'working_directory')
  # check that working directory is not currently in the filepath
  if not working_directory in file['file']:
    path = os.path.join(working_directory, file['file'])
  else:
    path = file['file']
  try:
    with open(path, 'r') as f:
      content = f.read()
    logger.info(f'Read file: {path}')
    response = [{'role': 'system', 'content': f'Read file: {path}\n\n{content}', 'resend': True}]
    print_msg(response)
    return response
  except Exception as e:
    logger.error(e)
    response = [{'role': 'system', 'content': f'Error reading file: {path}\n\n{e}'}]
    print_msg(response)
    return response