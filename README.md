# Toxic Bot

Toxic Bot is a bot for Telegram.

## Starting

I'm running application in Docker for production, and for local debug I use `make port` to run SSH tunnel to production database and start bot on host machine connecting to production database.

For containers management, I use my own utility called [op](https://github.com/slasyz/op).

### Using Docker, locally
- Install `docker` and `op` on local machine.
- Create file `/etc/toxic/config.json` based on `config.default.json` and edit it:
    - create random database password;
    - create Telegram token.
- Start it locally, there are two options:
    1. Deploy everything in container via `op deploy -e local`.
    2. Deploy dependencies in container and run bot on host machine:
        - run `op debug` to deploy dependencies containers;
        - run `make venv` to create virtual env and install dependencies;
        - run `make run` or press green triangle button in your IDE to start it.

### Using Docker, remotely
- Install docker on local and remote machine.
- On target machine create file `/etc/toxic/config.json` based on `config.default.json` and edit it.
    - create random database password;
    - create Telegram token.
- Deploy everything: `op deploy -e prod` on dev machine.

### Directly (locally or remotely)
- Install tmux on remote machine.
- Copy sources to remote machine.
- Create virtual env and install dependencies: `make venv`.
- Create database, initialize it manually.
- Run `cp config.default.json config.json` and specify all credentials in new file;
- Run `make tmux.start`, `make tmux.restart` or `./venv/bin/python main.py`


## License
[MIT](https://choosealicense.com/licenses/mit/)
