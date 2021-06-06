# Toxic Bot

Toxic Bot is a bot for Telegram.

## Starting

I'm running application in Docker for production, and for local debug I use `make port` to run SSH tunnel to production database and start bot on host machine connecting to production database.

### Using Docker, locally
- Install docker on local machine.
- Initialize stuff for Docker: `make init.local`.
- Create file `/etc/toxic/config.json` based on `config.default.json` and edit it:
    - create random database password;
    - create Telegram token.
- Start it locally, there are two options:
    1. Deploy everything in container via `make deploy.local`.
    2. Deploy dependencies in container and run bot on host machine:
        - run `make debug` to deploy dependencies containers;
        - run `make venv` to create virtual env and install dependencies;
        - run `make run` or press green triangle button in your IDE to start it.

### Using Docker, remotely
- Install docker on local and remote machine.
- On target machine create file `/etc/toxic/config.json` based on `config.default.json` and edit it.
    - create random database password;
    - create Telegram token.
- Initialize secrets by running `make init.prod` on dev machine.
- Deploy everything: `make deploy.prod` on dev machine.

### Directly (locally or remotely)
- Install tmux on remote machine.
- Copy sources to remote machine.
- Create virtual env and install dependencies: `make venv`.
- Create database, initialize it manually.
- Run `cp config.default.json config.json` and specify all credentials in new file;
- Run `make tmux.start`, `make tmux.restart` or `./venv/bin/python main.py`


## License
[MIT](https://choosealicense.com/licenses/mit/)
