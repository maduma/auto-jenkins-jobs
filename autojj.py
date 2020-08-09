import re
import collections
import settings
import jenkins_client
import gitlab_client
import random
import string

logger = settings.get_logger(__name__)

# maximum jenkins operations (create and update)
MAX_JENKINS_OPS = 2

# folder is jenkins folder and full_name is jenkins job full path 
Project = collections.namedtuple(
    'Project',
    'pipeline id full_name folder short_name git_http_url trigger_token',
    defaults=[False, 0] + [''] * 5,
    )


def process_event(event):
    if not is_repository_update(event):
        msg =  f"Can only handle GitLab 'repository_update' event: {str(event)}"
        logger.error(msg)
        return msg, 200

    project = parse_event(event)
    if project:
        if project.pipeline:
            logs = install_pipeline(project)
            return '\n'.join(logs), 200
        else:
            msg = f"No known Jenkins Pipeline found for {project.full_name}"
            return msg, 200

    return "Cannot parse event", 200


def is_repository_update(event):
    try: 
        if not event.get('event_name') == "repository_update":
            return False
    except AttributeError:
        # handle the case when event is not a dictionary
        logger.error(f'GitLab event is not an json object: {str(event)}')
        return False

    return True


def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(24)) 


def parse_event(event):
    path_with_namespace = event['project']['path_with_namespace']
    fields = path_with_namespace.split('/')

    if not len(fields) > 1:
        logger.error(f'Cannot get folder and short_name for {path_with_namespace}')
        return None

    folder, *_, short_name = path_with_namespace.split('/')
    full_name = '/'.join([folder, short_name])
    project_id = event['project_id']
    git_http_url = event['project']['git_http_url']

    project =  Project(
      id=project_id,
      full_name=full_name,
      folder=folder,
      short_name=short_name,
      git_http_url=git_http_url,
      trigger_token=random_string(),
    )

    jenkinsfile = gitlab_client.get_jenkinsfile(project)
    if jenkinsfile:
        pipeline = is_autojj_project(jenkinsfile)
        project = project._replace(pipeline=pipeline)
        folder = get_folder_setting(jenkinsfile)
        if folder:
            project = project._replace(folder=folder)
            full_name = '/'.join([folder, short_name])
            project = project._replace(full_name=full_name)

    return project


def is_autojj_project(jenkinsfile, types=settings.PROJECT_TYPES):
    # try to find 'known' groovy function call
    for type in types:
        if not re.match(r'\w+', type):
            logger.error(f'Project type: {type} is not a word')
            return False
        regex = r'(\s|^)({})(\s|\()'.format(type)
        pattern = re.compile(regex)
        found = pattern.search(jenkinsfile)
        if found:
            return found[2]

    logger.info('No known groovy call found in Jenkinsfile')
    return False

def get_folder_setting(jenkinsfile):
    regex = r'AUTOJJ:JENKINS_FOLDER:(\w+)'
    match = re.search(regex, jenkinsfile)
    if match:
        return match.group(1)
    else:
        return None

def install_pipeline(project, ops_log=None, ops=0):
    if ops > MAX_JENKINS_OPS:
        msg = f'Try more than {MAX_JENKINS_OPS} times, check errors'
        logger.error(msg)
        ops_log.append(msg)
        return ops_log

    if ops_log == None:
        ops_log = []
    state = jenkins_client.get_pipeline_state(project)
    if not state.is_folder_exists:
        ops_log.append(jenkins_client.create_folder(project))
    elif not state.is_pipeline_exists:
        ops_log.append(jenkins_client.create_pipeline(project))
        ops_log.append(gitlab_client.install_webhook(project))
    elif not state.is_folder_updated:
        ops_log.append(jenkins_client.update_folder(project))
    elif not state.is_pipeline_updated:
        ops_log.append(jenkins_client.update_pipeline(project))
    else: 
        if not len(ops_log):
            msg = f'Pipeline {project.full_name} exists and up-to-date, nothing to do'
            logger.info(msg)
            ops_log.append(msg)
        return ops_log

    return install_pipeline(project, ops_log=ops_log, ops=ops + 1)
