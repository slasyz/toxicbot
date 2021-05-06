FROM postgres:13.2

# It would be nice to use image postgres:13.2 in stack/base.yml and mount migrations directory as a volume.
# But in this case it won't be possible to deploy stack to remote context because it will save local paths and try
# to use it on remote machine.
COPY migrations /docker-entrypoint-initdb.d/
