import logging
import re
import requests
import os
import jenkins_client
import gitlab_client

TOKEN = os.environ.get('GIT_PRIVATE_TOKEN','unknown')

logging.basicConfig(level=logging.INFO)

ACTION = 'action'
GO_ON = 'go_on'
NOP = None
CREATE_JOB = 'create_job'
UPDATE_JOB = 'update_job'
CREATE_FOLDER = 'create_folder'
BUILD_JOB = 'build_job'

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


def get_project(post_data):
    if not post_data or not post_data.get('event_name') == "repository_update":
        logging.error('Cannot get job name from post data')
        logging.debug(f'Bad input: {post_data}')
        return None

    namespace = post_data['project']['namespace']
    short_name = post_data['project']['name']
    name = '/'.join([namespace, short_name])
    git_url = post_data['project']['git_http_url']
    id = post_data['project_id']
    return { "id": id, "name": name, 'git_url': git_url , "namespace": namespace, "short_name": short_name }

def is_autojj_project(jenkinsfile, methods):
    # look for groovy method
    for word in methods:
        if not re.match(r'\w+', word):
            return False
        regex = r'(\s|^)({})(\s|\()'.format(word)
        pattern = re.compile(regex)
        found = pattern.search(jenkinsfile)
        if found:
            return found[2]
    return False

def get_raw_gitlab_jenkinsfile_url(project):
    project_url = project['git_url']
    project_id = project['id']
    base = ('/').join(project_url.split('/')[:3])
    return base + '/api/v4/projects/{}/repository/files/Jenkinsfile/raw?ref=master'.format(project_id)

def get_jenkinsfile(project, token):
    url = get_raw_gitlab_jenkinsfile_url(project)
    resp = requests.get(url, headers={'PRIVATE-TOKEN': token}, timeout=2)
    if resp.status_code == 200:
        return resp.text
    else:
        logging.error('Cannot get Jenkins file')
        return None

# to test
def get_job_state(project):
    pipeline_xml = jenkins_client.is_pipeline_exists(project['name'])
    is_folder_exists = jenkins_client.is_folder_exists(project['namespace'])
    is_pipeline_up_to_date = False
    if pipeline_xml:
        is_pipeline_up_to_date = jenkins_client.is_job_up_to_date_xml(pipeline_xml)
    return (pipeline_xml, is_folder_exists, is_pipeline_up_to_date)

# recurtion and yield -> need to use 'yield from'
def actions(project, action={ACTION: NOP, GO_ON: True}):
    if action[ACTION] != NOP:
        yield action
    if action[GO_ON]:
        state = get_job_state(project)
        action = next_action(*state)
        yield from actions(project, action)

# to test
def do_jenkins_actions(project):
    logs = []
    for action in actions(project):
        if action[ACTION] == CREATE_JOB:
            name = project['name']
            jenkins_client.create_job(project)
            jenkins_client.build_job(name)
            if not gitlab_client.is_hook_installed(project):
                gitlab_client.install_jenkins_hook(project)
            logs.append('Project Created, gitlab hook installed and Build Started')
        elif action[ACTION] == UPDATE_JOB:
            jenkins_client.update_job(project)
            logs.append('Project Updated')
        elif action[ACTION] == CREATE_FOLDER:
            name = project['namespace']
            jenkins_client.create_folder(name)
            logs.append('Folder Created')
        elif action[ACTION] == BUILD_JOB:
            name = project['namespace']
            jenkins_client.build_job(name)
            logs.append('Start Job Build')
    return ', '.join(logs)

# to test !
def process_event(event):
    project = get_project(event)
    if project:
        jenkinsfile = get_jenkinsfile(project, TOKEN)
        if jenkinsfile:
            project_type = is_autojj_project(jenkinsfile, methods=['mulePipeline'])
            if project_type:
                project['project_type'] = project_type
                logs = do_jenkins_actions(project)
                return "Event processed: " + logs
            else:
                return "Cannot find project type in Jenkinsfile", 200
        else:
            return 'Cannot access Jenkinsfile (do not exists?) or is not and Auto Jenkins Project', 200
    return "Cannot find project in the event", 200