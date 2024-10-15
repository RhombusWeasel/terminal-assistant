from utils.tools import new_tool, tools
from utils.async_ai import Agent
from utils.logger import Logger
from utils.prompt_tools import print_msg
import json, time, uuid

logger = Logger('chain_actions')
funcs = [value['schema'] for key, value in tools.items()]

@new_tool('chain_actions', {
    'name': 'chain_actions',
    'description': 'If the user has asked you to perform a multi step series of actions then use this tool. Executes a chain of actions in sequence to achieve the users goal. Each action in the chain must be valid and from this list and be presented as an object in the following format: { "action": "action_name", "args": {"arg_name": "arg_value"...} }.',
    'parameters': {
        'type': 'object',
        'properties': {
            'actions': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'action': {
                            'type': 'string',
                            'description': 'The name of the action to perform.'
                        },
                        'args': {
                            'type': 'object',
                            'description': 'The arguments to pass to the action. Each set of arguments for the action must be within this object.'
                        }
                    },
                    'required': ['action', 'args']
                },
                'description': 'A list of actions to perform in sequence.'
            }
        },
        'required': ['actions']
    }
})
def chain_actions(data):
    results = []
    chk_prompt = f'Here is a summary of the actions you have been asked to perform: {json.dumps(data["actions"], indent=2)}.'
    print(f"Agent wants to perform a chain of {len(data['actions'])} actions.")
    for i, action in enumerate(data['actions']):
      print(f"  {i+1}. {action['action']}")
      if action['action'] not in tools:
        logger.error(f"Action '{action['action']}' not found.")
        return [{'role': 'system', 'content': f"Error: Action '{action['action']}' not found."}]
      for arg in action['args']:
        print(f"    {arg}: {action['args'][arg]}")
    
    response = input("Do you want to continue? (y/n): ")
    if response.lower() != 'y':
      return [{'role': 'system', 'content': 'Chain aborted by user.'}]

    # Pop each action off the list and execute it
    while len(data['actions']) > 0:
        action = data['actions'].pop(0)
        results.extend(tools[action['action']]['function'](action['args']))

        # Create an agent to check we are still on track
        if len(data['actions']) > 0:
            agent = Agent()
            m = [
                {"role": "system", "content": chk_prompt},
                {"role": "system", "content": f"Last action: {action['action']}\n Last Args: {json.dumps(action['args'], indent=2)}"},
                {"role": "system", "content": f"Current results: {json.dumps(results, indent=2)}"},
                {"role": "system", "content": f"Next action: {data['actions'][0]['action']}\n Next Args: {json.dumps(data['actions'][0]['args'], indent=2)}"},
                {"role": "system", "content": "Please confirm that the results are as expected and that you are sure the next action will succeed based on any new information available in the results.  If there is any new information available that will make the next action fail, please respond with the corrected function call.  Pay close attention to details here, have we read a file or run a command that tells us our next step is incorrect?"}
            ]
            response = agent.get_response(m, functions=funcs, temperature=0.3)['text']
            msg = [{'role': 'assistant', 'content': response}]
            if 'content' in response and response['content'] != None:
                print_msg([{'role': 'assistant', 'content': response['content']}], filepath='output/chain.json')
            if 'function_call' in response:
                if response['function_call']['name'] == data['actions'][0]['action']:
                    key = response['function_call']['name']
                    args = response['function_call']['arguments']
                    if type(args) != dict:
                        try:
                            args = json.loads(args)
                        except:
                            args = {}
                    print(f"Function call: {response['function_call']['name']} with args: {response['function_call']['arguments']}")
                    data['actions'][0]['args'] = args
            time.sleep(0.5)

    
    results[-1]['resend'] = True
    return results