# Toxic Bot

Toxic Bot is a bot for Telegram.

## Starting

### In container locally
- Install docker on local machine.
- Join Swarm: `docker swarm init`.
- Initialize secrets: `make init.local`.
- Start it locally, there are two options:
    1. Deploy everything in container via `make deploy.local`.
    2. Deploy dependencies in container and run bot on host machine:
        - `make debug` to deploy dependencies;
        - `cp config.debug.json config.json`;
        - open `config.json` and specify all credentials;
        - `make venv` to create virtual env and install dependencies;
        - `./venv/bin/python main.py` to start it.

### In container remotely
- Install docker on local and remote machine.
- Join Swarm on remote machine: `docker swarm init`.
- Initialize secrets: `make init.prod`.
- Deploy everything: `make deploy.prod`.

### On host machine (locally or remotely)
- Install tmux on remote machine.
- Copy sources to remote machine.
- Create virtual env and install dependencies: `make venv`.
- Run `make tmux.start`, `make tmux.restart` or `./venv/bin/python main.py`


## License
[MIT](https://choosealicense.com/licenses/mit/)
