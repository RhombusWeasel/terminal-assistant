# Terminal Assistant

This is a terminal assistant project that provides assistance to users in achieving their desired results. It is designed to run in a terminal environment.

## Features

- Installation of Apache2 web server
- Displaying the current time

## Getting Started

To get started with the terminal assistant, follow the steps below:

1. Clone the repository
2. Navigate into the folder and copy the config file `cp ./config.ini.example ./config.ini`
3. Add your API key to the config file and choose your model
4. Run `./install.sh` this will create the venv and install the dependencies

For future sessions you can use `./launch.sh`

## Usage

Once the terminal assistant is running, you can interact with it by entering commands:

- `help`: Display the available commands
- `tools`: List the available tools
- `clear`: Clear the message history
- `quit`: Exit the terminal assistant

Anything not in the above list or the configured alieses for them is treated as a query and will be sent to openAI

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).