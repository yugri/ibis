from fabric.api import *

env.hosts = ['139.59.138.205']
env.user = 'root'


# def push_changes():
#     with lcd('/home/yuri/dev/ibis_crawl_engine'):
#         local('git push origin master')


def update_project():
    with cd('/webapps/crawler/ibis_crawl_engine'):
        run('git pull')
        with prefix('source /webapps/crawler/bin/activate'):
            run('python manage.py migrate --noinput')
            run('python manage.py collectstatic --noinput')


def restart_webserver():
    sudo('supervisorctl restart all')


def deploy():
    # push_changes()
    update_project()
    restart_webserver()