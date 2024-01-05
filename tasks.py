from fabric import Connection
from invoke import task


@task
def deploy(c, t='user@server', project_dir="~/deployments/toxic", logs_prefix="~/logs/toxic"):
    conn = Connection(t)

    # Sources
    c.run(f'rsync -avuz ./toxic/ {t}:{project_dir}/toxic/')
    c.run(f'rsync -avuz ./resources/ {t}:{project_dir}/resources/')
    c.run(f'scp ./main.py ./config.json ./pyproject.toml {t}:{project_dir}')

    # Systemd service files
    c.run(f'scp ./systemd/toxic-*.service {t}:~/.config/systemd/user/')
    conn.run('chmod 0600 ~/.config/systemd/user/toxic-*.service')
    conn.run(f'sed -i "s|{{{{ logs_prefix }}}}|$(readlink -f {logs_prefix})|g" ~/.config/systemd/user/toxic-*.service')
    conn.run(f'sed -i "s|{{{{ project_dir }}}}|$(readlink -f {project_dir})|g" ~/.config/systemd/user/toxic-*.service')

    # Update deps
    conn.run(f'cd {project_dir} && poetry update')

    # Restarting
    conn.run('systemctl --user daemon-reload')
    conn.run('systemctl --user restart toxic-main')
    conn.run('systemctl --user restart toxic-server')
