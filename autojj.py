import logging
import re

logging.basicConfig(level=logging.DEBUG)

ACTION = 'action'
GO_ON = 'go_on'
NOP = None
CREATE_JOB = 'create_job'
UPDATE_JOB = 'update_job'
CREATE_FOLDER = 'create_folder'

def next_action(job_exists, folder_exists, job_up_to_date=False):
    action = {}

    if folder_exists:
        if job_exists:
            if job_up_to_date:
                action = {ACTION: NOP, GO_ON: False}
            else:
                action = {ACTION: UPDATE_JOB, GO_ON: False}
        else:
            action = {ACTION: CREATE_JOB, GO_ON: False}
    elif job_exists:
        logging.error(f'Bad input: job_exists={job_exists} but not folder. folder_exists={folder_exists}')
        action = {ACTION: NOP, GO_ON: False}
    else:
        action = {ACTION: CREATE_FOLDER, GO_ON: True}

    if not action:
        logging.error(f'Bad input: job_exists={job_exists} , folder_exists={folder_exists} , job_up_to_date={job_up_to_date}')
        action = {ACTION: NOP, GO_ON: False}
    else:
        logging.debug(f'job_exists={job_exists} , folder_exists={folder_exists} , job_up_to_date={job_up_to_date}')
        logging.info(f'ACTION: {action[ACTION]}, GO_ON: {action[GO_ON]}')

    return action


def get_job(post_data):
    if not post_data or not post_data.get('event_name') == "repository_update":
        logging.error('Cannot get job name from post data')
        logging.debug(f'Bad input: {post_data}')
        return None

    name = '/'.join([
        post_data['project']['namespace'],
        post_data['project']['name'],
        ])
    git_url = post_data['project']['git_http_url']
    return { "name": name, 'git_url': git_url }

def is_autojj_project(jenkinsfile, methods):
    # look for groovy method
    for word in methods:
        if not re.match(r'\w+', word):
            return False
        regex = r'(\s|^){}(\s|\()'.format(word)
        pattern = re.compile(regex)
        if pattern.search(jenkinsfile):
            return True
    return False

def get_raw_gitlab_jenkinsfile_url(git_url):
    return git_url[:-4] + '/-/raw/master/Jenkinsfile'