import logging
import re
import requests
import os
import jenkins_client
import gitlab_client
import settings
import collections

# folder is jenkins folder and full_name is jenkins job full path 
Project = collections.namedtuple('Project', 'id full_name folder short_name git_http_url pipeline', defaults=[0] + [''] * 4 + [False])
# maximum jenkins operations (create and update)
MAX_JENKINS_OPS = 2

def parse_event(event):

    full_name = event['project']['path_with_namespace']
    folder, short_name = full_name.split('/')
    project_id = event['project_id']
    git_http_url = event['project']['git_http_url']

    jenkinsfile = gitlab_client.get_jenkinsfile(Project(id=project_id, git_http_url=git_http_url))
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
            logs = install_pipeline(project)
            return logs, 200
        else:
            return "Unknown Jenkins Pipeline", 200
    return "Cannot parse project in the GitLab event", 500

def install_pipeline(project, log=None, ops=0):
    if ops > MAX_JENKINS_OPS:
        log.append(f'Try more than {MAX_JENKINS_OPS} times, check errors')
        return log

    if log == None:
        log = []
    state = jenkins_client.get_pipeline_state(project)
    if not state.is_folder_exists:
        log.append(jenkins_client.create_folder(project))
    elif not state.is_folder_updated:
        log.append(jenkins_client.update_folder(project))
    elif not state.is_pipeline_exists:
        log.append(jenkins_client.create_pipeline(project))
        log.append(gitlab_client.install_web_hook(project))
    elif not state.is_pipeline_updated:
        log.append(jenkins_client.update_pipeline(project))
    else: 
        if not len(log):
            log.append(f'Pipeline {project.full_name} exists and up-to-date, nothing to do')
        return log

    return install_pipeline(project, log=log, ops=ops + 1)
