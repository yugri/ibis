from fabric.api import *

# env.hosts = ['139.59.138.205']
# env.hosts = ['95.85.40.149']
env.roledefs = {
    'prod': ['95.85.40.149'],
    'dev': ['139.59.138.205'],
}
env.user = 'root'


def push_changes():
    with lcd('/home/yuri/dev/ibis_crawl_engine'):
        local('git push origin master')


def update_project_prod():
    with cd('/var/www/crawler'):
        run('git pull')
        with prefix('source /var/www/venv/bin/activate'):
            run('python manage.py migrate --noinput')
            run('python manage.py collectstatic --noinput')


def update_project_dev():
    with cd('/webapps/crawler/ibis_crawl_engine'):
        run('git pull')
        with prefix('source /webapps/crawler/bin/activate'):
            run('python manage.py migrate --noinput')
            run('python manage.py collectstatic --noinput')


def restart_webserver():
    sudo('supervisorctl restart all')


@roles('dev')
def deploy_dev():
    push_changes()
    update_project_dev()
    restart_webserver()


@roles('prod')
def deploy_prod():
    push_changes()
    update_project_prod()
    restart_webserver()