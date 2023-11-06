# Terminal Assistant

This is a terminal assistant project that provides assistance to users in achieving their desired results. It is designed to run in a terminal environment.

## Features

- Google search, the assistant can search google and summarize the top 5 pages it finds
- Memory management, the assistant can remember things you tell it and recall them later (Requires a reverie account)
- Sandboxed execution, the assistant can run commands (with permission) in a sandboxed environment and return the output to you, outputs are included in the chat so you and the assistant can see the results

## Getting Started

To get started with the terminal assistant, follow the steps below:

1. Clone the repository
2. Navigate into the folder and copy the config file `cp ./config.ini.example ./config.ini`
3. Add your API key to the config file and choose your model
4. Run `./install.sh` this will create the venv and install the dependencies
5. Edit the reset_prefs.py file and add any initial memory entries you want the assistant to know.
   The data should be a list of objects containing the information with tags.
6. Execute `python3 reset_prefs.py` to add your seed data to reverie

For future sessions you can use `./launch.sh`

## Usage

Once the terminal assistant is running, you can interact with it by entering commands:

- `help`: Display the available commands
- `tools`: List the available tools
- `clear`: Clear the message history
- `quit`: Exit the terminal assistant
- `cmd`: Switch to command mode and run commands in the sandbox

Anything not in the above list or the configured alieses for them is treated as a query and will be sent to openAI for processing. For the most part the AI can handle any given request but for optimal results I find it is best to hint at the function you want to use. For example, if you want to search google for something, you can say "search google for" or "Look online for" and then your query. This will help the AI understand what you want it to do and will give you better results.

The memory system relies on two functions exposed to the llm, mem_search and mem_archive. mem_search will make a request to Reverie and bring back the 2 closest contextual matches to the llm's query. mem_archive will take the data from the llm along with instructions for it's storage and pass it to a 2nd agent who is responsible for keeping data in the archive clustered together by type to provide better recollection.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
