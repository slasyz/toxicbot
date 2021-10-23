import os
import sys
from datetime import datetime
from subprocess import PIPE, Popen

import boto3
from botocore.exceptions import ClientError

from toxic.config import Config
from toxic.helpers.log import init_sentry

BUCKET_NAME = "toxicbot"


def dump_table(hostname, port, dbname, username, password, filename):
    command = 'pg_dump --data-only --column-inserts -h {} -p {} -U {} -d {} | gzip > {}'.format(
        hostname, port, username, dbname, filename,
    )

    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, env={
        'PGPASSWORD': password,
    })
    p.communicate('{}\n'.format(password).encode('utf-8'))

    rc = p.wait()
    if rc != 0:
        raise Exception('Return code {}.'.format(rc))


def upload_file(filename, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(filename)

    s3_client = boto3.client('s3')
    response = s3_client.upload_file(filename, bucket, object_name)
    print(dir(response))
    print(response)
    return True


def __main__():
    now = datetime.now().strftime('%Y%m%d-%H%M%S')
    basename = 'toxicbot-s3-backup-{}.sql.gz'.format(now)
    filename = '/tmp/' + basename
    s3_name = 'backup-db/' + basename

    config_files = ['config.json', '/etc/toxic/config.json']
    config = Config.load(config_files)

    init_sentry(config['sentry']['dsn'])

    print('-> pg_dump', file=sys.stderr)
    dump_table(
        config['database']['host'],
        config['database']['port'],
        config['database']['name'],
        config['database']['user'],
        config['database']['pass'],
        filename,
    )

    print('-> uploading', file=sys.stderr)
    try:
        upload_file(filename, BUCKET_NAME, s3_name)
    except ClientError as e:
        print('Client error: {}'.format(e), file=sys.stderr)


if __name__ == '__main__':
    __main__()
