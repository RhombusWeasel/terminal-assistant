from utils.logger import Logger
from utils.tools import new_tool
from utils.prompt_tools import print_msg
import configparser

logger = Logger('tool_write')
conf = configparser.ConfigParser()
conf.read('config.ini')
working_directory = conf.get('term', 'working_directory')

@new_tool('write_file', {
  'name': 'write_file',
  'description': 'Writes to a file.',
  'parameters': {
    'type': 'object',
    'properties': {
      'file': {
        'type': 'string',
        'description': 'The path to the file to write to.',
      },
      'content': {
        'type': 'string',
        'description': 'The content to write to the file.',
      }
    },
    'required': ['file', 'content']
  }
})
def write_file(data):
  path = data['file']
  if not working_directory in path:
    path = working_directory + '/' + path
  with open(path, 'w') as f:
    f.write(data['content'])
  logger.info(f'Wrote to file: {path}')
  response = [{'role': 'system', 'content': f'Wrote to file: {path}'}]
  print_msg(response)
  return response