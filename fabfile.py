from fabric.api import run, env, cd, sudo, prefix
from contextlib import contextmanager as _contextmanager

env.activate = 'workon Interactale'
env.directory = '~/Apps/Interactale/TaleHouse'


@_contextmanager
def virtualenv():
    with prefix(env.activate):
        yield


def deploy():
    with cd(env.directory):

        run('git pull origin master')

        with virtualenv():
            run('pip install MySQL-python==1.2.5')
            run('pip install -r ' + env.directory + '/requirements.txt')
            run('python manage.py syncdb')
            run('python manage.py migrate Teller')
            run('python manage.py collectstatic')
            run('python manage.py compilemessages')

        # sudo('service apache2 restart')
