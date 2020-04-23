import logging
import re
import requests
import os
import jenkins_client
import gitlab_client
import settings
import collections

ACTION = 'action'
GO_ON = 'go_on'
NOP = None
CREATE_JOB = 'create_job'
UPDATE_JOB = 'update_job'
CREATE_FOLDER = 'create_folder'
BUILD_JOB = 'build_job'

# folder is jenkins folder and full_name is jenkins job full path (folder + name)
Project = collections.namedtuple('Project', 'id full_name folder short_name git_http_url pipeline')
PipelineState = collections.namedtuple('PipelineState', 'is_folder_exists, is_pipeline_exists is_folder_updated is_pipeline_updated')
ALL_GOOD_STATE = PipelineState(is_folder_exists=True, is_pipeline_exists=True, is_folder_updated=True, is_pipeline_updated=True)


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

def parse_event(event):

    full_name = event['project']['path_with_namespace']
    folder, short_name = full_name.split('/')
    project_id = event['project_id']
    git_http_url = event['project']['git_http_url']

    api_url = get_raw_gitlab_jenkinsfile_url(project_id, git_http_url)
    jenkinsfile = get_jenkinsfile(api_url, settings.GITLAB_PRIVATE_TOKEN)
    pipeline = is_autojj_project(jenkinsfile, types=settings.PROJECT_TYPES)
    
    project = Project(
      id = project_id,
      full_name = full_name,
      folder = folder,
      short_name = short_name,
      git_http_url = git_http_url,
      pipeline = pipeline,
    )

    return project

def is_autojj_project(jenkinsfile, types):
    if not jenkinsfile:
        return False
    # look for groovy method
    for type in types:
        if not re.match(r'\w+', type):
            logging.error('Project type: %s is not a word' % type)
            return False
        regex = r'(\s|^)({})(\s|\()'.format(type)
        pattern = re.compile(regex)
        found = pattern.search(jenkinsfile)
        if found:
            return found[2]
    return False

def get_raw_gitlab_jenkinsfile_url(project_id, project_url):
    base = ('/').join(project_url.split('/')[:3])
    return base + '/api/v4/projects/{}/repository/files/Jenkinsfile/raw?ref=master'.format(project_id)

def get_jenkinsfile(api_url, token):
    resp = requests.get(api_url, headers={'PRIVATE-TOKEN': token}, timeout=2)
    if resp.status_code == 200:
        return resp.text
    else:
        logging.error('Cannot get Jenkins file ' + str(resp.reason))
        return None

# to test
def get_job_state(project):
    pipeline_xml = jenkins_client.is_pipeline_exists(project.full_name)
    is_pipeline_exits = pipeline_xml
    is_folder_exists = jenkins_client.is_folder_exists(project.folder)
    is_pipeline_up_to_date = False
    if pipeline_xml:
        is_pipeline_up_to_date = jenkins_client.is_job_up_to_date_xml(pipeline_xml)
    return (is_pipeline_exits, is_folder_exists, is_pipeline_up_to_date)

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
        type = action[ACTION] 
        logging.info('handle action: ' + type)
        if type == CREATE_JOB:
            jenkins_client.create_job(project)
            if not gitlab_client.is_hook_installed(project):
                gitlab_client.install_jenkins_hook(project)
            logs.append('Project Created, gitlab hook installed and Build Started')
        elif type == UPDATE_JOB:
            jenkins_client.update_job(project)
            logs.append('Project Updated')
        elif type == CREATE_FOLDER:
            jenkins_client.create_folder(project.folder)
            logs.append('Folder Created ' + project.folder)
        else:
            logs.append('Unknow action ' + type)
    return ', '.join(logs)

def is_repository_update(event):
    try: 
        if not event.get('event_name') == "repository_update":
            return False
    except AttributeError:
        # handle the case when event is not a dictonary
        return False
    return True

def process_event(event):
    if not is_repository_update(event):
        return "Can only handle GitLab 'repository_update' event", 400

    project = parse_event(event)
    if project:
        if project.pipeline:
            logs = do_jenkins_actions(project)
            return "Event processed: " + logs , 200
        else:
            return "Unknown Jenkins Pipeline", 200
    return "Cannot parse project in the GitLab event", 500

def get_pipeline_state(project):
    return PipelineState(*[True]*4)

def install_pipeline(project):
    log = []
    state = get_pipeline_state(project)
    print(state)

    if state == ALL_GOOD_STATE:
        log.append(f'Pipeline {project.full_name} exists and up-to-date, nothing to do')
        return log

    if not state.is_folder_exists:
        log.append(jenkins_client.create_folder(project))
        log.append(jenkins_client.create_pipeline(project))
        log.append(gitlab_client.install_web_hook(project))
        return log

    if not state.is_pipeline_exists:
        if not state.is_folder_updated:
            log.append(jenkins_client.update_folder(project))
        log.append(jenkins_client.create_pipeline(project))
        log.append(gitlab_client.install_web_hook(project))
        return log

    if not state.is_pipeline_updated:
        log.append(jenkins_client.update_pipeline(project))
        return log

    if not state.is_folder_updated:
        log.append(jenkins_client.update_folder(project))
        return log
