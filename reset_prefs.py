from utils.memory_client import MemoryClient
import configparser

conf = configparser.ConfigParser()
conf.read('config.ini')

if __name__ == '__main__':
    import json
    memories = [
        {
            "tags": ["coding", "scripting", "programming"],
            "global": {
                "var_naming": "snake_case",
                "indentation": "2 spaces",
                "line_length": "80",
                "docstring": "google",
                "paradigm": "functional",
            },
        },
        {
            "tags": ["family", "parents", "siblings"],
            "mother": {
                "name": "Your mother",
                "location": "Someplace",
                "birthday": "Some date",
                "interests": ["interest 1", "interest 2", "interest 3"],
            },
            "father": {
                "name": "Your father",
                "location": "Someplace",
                "birthday": "Some date",
                "interests": ["interest 1", "interest 2", "interest 3"],
            },
        },
        {
            "tags": ["food", "recipes", "cooking"],
            "favourites": {
                "breakfast": "eggs and bacon",
                "lunch": "a sandwich",
                "dinner": "steak with peppercorn sauce",
                "dessert": "creme brulee",
            },
        },
    ]
    print('Initializing MemoryClient')
    client = MemoryClient(conf['memory']['base_url'])
    print(client.login())
    print(client.view_repositories())
    client.delete_repository('terminal-assistant')
    client.create_repository('terminal-assistant')

    for memory in memories:
        print(client.add_text_if_unique('terminal-assistant', json.dumps(memory)))
    
    print(client.fetch_repository('terminal-assistant'))
    print(client.search('terminal-assistant', 'Mother date of birth'))