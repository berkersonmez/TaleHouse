from fabric.api import run, env, cd, sudo, prefix, local
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
            run('python manage.py migrate captcha')
            run('python manage.py migrate default')
            run('python manage.py collectstatic')
            run('python manage.py compilemessages')

        run('supervisorctl restart Interactale')


def setup_dev():
    # run 'pip install Fabric==1.10.1' before this
    local('python manage.py syncdb')
    local('python manage.py migrate Teller')
    local('python manage.py migrate captcha')
    local('python manage.py migrate default')
    local('python manage.py collectstatic')
    local('python manage.py compilemessages')