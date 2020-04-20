import logging
import re
import requests
import os
import jenkins_client
import gitlab_client
import settings

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

class Project:
    def __repr__(self):
        return """
        Project
        -------
        id:           {id}
        full_name:    {full_name}
        folder:       {folder}
        short_name:   {short_name}
        git_http_url: {git_http_url}
        git_ssh_url:  {git_ssh_url}
        -------
        """.format(
            id = self.id,
            full_name = self.full_name,
            folder = self.folder,
            short_name = self.short_name,
            git_http_url = self.git_http_url,
            git_ssh_url = self.git_ssh_url,
            )

def get_project(event):

    namespace = event['project']['namespace']
    folder, short_name = event['project']['path_with_namespace'].split('/')
    name = event['project']['path_with_namespace']
    full_name = event['project']['path_with_namespace']
    git_url = event['project']['git_http_url']
    id = event['project_id']
    
    project = Project()
    project.id = event['project_id']
    project.full_name = event['project']['path_with_namespace']
    project.folder, project.short_name = project.full_name.split('/')
    project.git_http_url = event['project']['git_http_url']
    project.git_ssh_url = event['project']['git_ssh_url']

    old_type_project =  { "id": id, "name": name, 'folder': folder, 'git_url': git_url , "namespace": namespace, "short_name": short_name , "full_name": full_name }

    jenkinsfile = get_jenkinsfile(old_type_project, settings.GITLAB_PRIVATE_TOKEN)
    project.pipeline = is_autojj_project(jenkinsfile, types=settings.PROJECT_TYPES)

    print(project)
    
    return old_type_project

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

def get_raw_gitlab_jenkinsfile_url(project):
    project_url = project['git_url']
    project_id = project['id']
    base = ('/').join(project_url.split('/')[:3])
    return base + '/api/v4/projects/{}/repository/files/Jenkinsfile/raw?ref=master'.format(project_id)

def get_jenkinsfile(project, token):
    api_url = get_raw_gitlab_jenkinsfile_url(project)
    resp = requests.get(api_url, headers={'PRIVATE-TOKEN': token}, timeout=2)
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

def is_repository_update(event):
    try: 
        if not event.get('event_name') == "repository_update":
            return False
    except AttributeError:
        # handle the case when event is not a dictonary
        return False
    return True

# to test !
def process_event(event):
    if not is_repository_update(event):
        return "Can only handle GitLab 'repository_update' event", 400

    project = get_project(event)
    if project:
        jenkinsfile = get_jenkinsfile(project, settings.GITLAB_PRIVATE_TOKEN)
        if jenkinsfile:
            project_type = is_autojj_project(jenkinsfile, types=settings.PROJECT_TYPES)
            if project_type:
                project['project_type'] = project_type
                logs = do_jenkins_actions(project)
                return "Event processed: " + logs
            else:
                return "Cannot detect project type in Jenkinsfile", 200
        else:
            return 'Cannot access Jenkinsfile (do not exists)', 200
    return "Cannot find project in the gitlab event", 200