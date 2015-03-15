from fabric.api import run, env, cd, sudo, prefix
from contextlib import contextmanager as _contextmanager

env.activate = 'source /home/env/bin/activate'
env.directory = '/home/TaleHouse'


@_contextmanager
def virtualenv():
    with prefix(env.activate):
        yield


def deploy():
    with cd(env.directory):

        run('git pull origin master')

        with virtualenv():
            sudo('pip install MySQL-python==1.2.5')
            sudo('pip install -r ' + env.directory + '/requirements.txt')
            run('python manage.py migrate Teller')
            run('python manage.py collectstatic')
            run('python manage.py compilemessages')

        sudo('service apache2 restart')
