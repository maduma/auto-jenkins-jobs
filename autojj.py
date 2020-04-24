import re
import logging
import collections
import settings
import jenkins_client
import gitlab_client

# folder is jenkins folder and full_name is jenkins job full path 
Project = collections.namedtuple('Project', 'id full_name folder short_name git_http_url pipeline', defaults=[0] + [''] * 4 + [False])
# maximum jenkins operations (create and update)
MAX_JENKINS_OPS = 2

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

def is_repository_update(event):
    try: 
        if not event.get('event_name') == "repository_update":
            return False
    except AttributeError:
        # handle the case when event is not a dictonary
        return False
    return True

def parse_event(event):
    full_name = event['project']['path_with_namespace']
    folder, short_name = full_name.split('/')
    project_id = event['project_id']
    git_http_url = event['project']['git_http_url']

    project = Project(id=project_id, git_http_url=git_http_url)
    jenkinsfile = gitlab_client.get_jenkinsfile(project)
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
            logging.error(f'Project type: {type} is not a word')
            return False
        regex = r'(\s|^)({})(\s|\()'.format(type)
        pattern = re.compile(regex)
        found = pattern.search(jenkinsfile)
        if found:
            return found[2]
    return False

def install_pipeline(project, ops_log=None, ops=0):
    if ops > MAX_JENKINS_OPS:
        ops_log.append(f'Try more than {MAX_JENKINS_OPS} times, check errors')
        return ops_log

    if ops_log == None:
        ops_log = []
    state = jenkins_client.get_pipeline_state(project)
    if not state.is_folder_exists:
        ops_log.append(jenkins_client.create_folder(project))
    elif not state.is_folder_updated:
        ops_log.append(jenkins_client.update_folder(project))
    elif not state.is_pipeline_exists:
        ops_log.append(jenkins_client.create_pipeline(project))
        ops_log.append(gitlab_client.install_webhook(project))
    elif not state.is_pipeline_updated:
        ops_log.append(jenkins_client.update_pipeline(project))
    else: 
        if not len(ops_log):
            ops_log.append(f'Pipeline {project.full_name} exists and up-to-date, nothing to do')
        return ops_log

    return install_pipeline(project, ops_log=ops_log, ops=ops + 1)


