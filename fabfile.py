from fabric.api import local, env, cd, sudo
env.hosts = ['139.59.138.205']
env.user = 'git'
# The user account that owns the application files and folders.
owner = 'crawler'
app_name = 'ibis_crawl_engine'
app_directory = '/webapps/crawler/ibis_crawl_engine'
settings_file = 'ibis_crawl_engine.settings'


def run_tests():
    local('coverage run manage.py test -v 2 --settings=settings.test')


def deploy():
    """
    Deploy the app to the remote host.
    Steps:
        1. Change to the app's directory.
        2. Pull changes from master branch in git.
        3. Activate virtualenv.
        4. Run pip install using the requirements.txt file.
        5. Run South migrations.
        6. Restart gunicorn WSGI server using supervisor.
    """
    with cd(app_directory):
        sudo('git pull', user=owner)
        venv_command = 'source ../bin/activate'
        pip_command = 'pip install -r requirements.txt'
        sudo('%s && %s' % (venv_command, pip_command), user=owner)
        migrate_command = 'python manage.py migrate --all ' \
                        '--settings=%s' % settings_file
        sudo('%s && %s' % (venv_command, migrate_command), user=owner)
        sudo('supervisorctl restart all')