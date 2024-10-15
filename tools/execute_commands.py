import os
import pty
import select
import configparser
import colorama

from utils.tools import new_tool
from utils.logger import Logger
from utils.prompt_tools import print_msg

logger = Logger('tool_execute')
conf = configparser.ConfigParser()
conf.read('config.ini')

colorama.init()

os_version = conf.get('term', 'os_version')
working_directory = conf.get('term', 'working_directory')

# Create the pty session outside of the function call
master, slave = pty.openpty()


def read_output(master_fd):
    output = ''
    while True:
        r, _, _ = select.select([master_fd], [], [], 0.1)
        if r:
            data = os.read(master_fd, 1024).decode('utf-8')
            if not data:
                break
            output += data
        else:
            break
    return output


def process_commands(commands):
    responses = []
    # execute the commands
    for command in commands:
        try:
            pid = os.fork()
            if pid == 0:  # Child process
                os.close(master)
                os.dup2(slave, 1)  # Redirect stdout to slave
                os.dup2(slave, 2)  # Redirect stderr to slave
                os.execv('/bin/bash', ['/bin/bash', '-c', command])
            else:  # Parent process
                out_str = ''
                while True:
                    r, _, _ = select.select([master], [], [], 0.1)
                    if r:
                        data = os.read(master, 1024).decode('utf-8')
                        if not data:
                            break
                        out_str += data
                    else:
                        pid, status = os.wait()
                        if pid != -1:
                            break
                responses.append({'role': 'system', 'content': f'{command}\n{out_str}\nCommand executed successfully.'})
        except Exception as e:
            responses.append({'role': 'system', 'content': f'Failed to execute command: {command}'})
            responses.append({'role': 'system', 'content': str(e)})
    for response in responses:
        print_msg([response], filepath='output/exe.json')
    return responses


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
def execute_commands(comm, override=False):
    if 'commands' not in comm:
        return
    if override:
        return process_commands(comm['commands'])
    commands = comm['commands']
    print(f'{colorama.Fore.RED}Terminal Assistant wants to execute the following commands:{colorama.Style.RESET_ALL}')
    for command in commands:
        print(f'  {command}')
    print('Do you want to execute these commands? (y/n)')
    answer = input('> ').strip()
    if answer.lower() == 'y':
        return process_commands(commands)
    else:
        return []

if __name__ == '__main__':
    r = execute_commands({'commands': ['ls', 'pwd', 'cd .. && ls', 'pwd']})
    print(r)
