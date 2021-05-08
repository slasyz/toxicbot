# Toxic Bot

Toxic Bot is a bot for Telegram.

## Starting

I'm running application in Docker for production, and for local debug I use `make port` to run SSH tunnel to production database and start bot on host machine connecting to production database.

### In container locally
- Install docker on local machine.
- Join Swarm: `docker swarm init`.
- Initialize secrets: `make init.local`.
- Start it locally, there are two options:
    1. Deploy everything in container via `make deploy.local`.
    2. Deploy dependencies in container and run bot on host machine:
        - run `make debug` to deploy dependencies;
        - run `cp config.debug.json config.json` and specify all credentials in new file;
        - run `make venv` to create virtual env and install dependencies;
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
- Create database, initialize it manually.
- Run `cp config.debug.json config.json` and specify all credentials in new file;
- Run `make tmux.start`, `make tmux.restart` or `./venv/bin/python main.py`


## License
[MIT](https://choosealicense.com/licenses/mit/)
