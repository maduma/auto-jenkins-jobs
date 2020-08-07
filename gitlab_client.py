import os
import requests
import settings

logger = settings.get_logger(__name__)


def is_gitlab_online(gitlab_url=settings.GITLAB_URL, token=settings.GITLAB_PRIVATE_TOKEN):
    url = f'{gitlab_url}/api/v4/user'

    try:
        resp = requests.get(url, headers={'PRIVATE-TOKEN': token}, timeout=2)
        if resp.status_code == 200:
            if resp.json()['is_admin']:
                return {'status': 'online'}
            else:
                return {'status': 'degraded', 'message': 'requires higher privileges than provided'}
        else:
            return {'status': 'error', 'message': resp.reason}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def get_webhooks(project, token=settings.GITLAB_PRIVATE_TOKEN):
    gitlab_url = '/'.join(project.git_http_url.split('/')[:3])
    url = f'{gitlab_url}/api/v4/projects/{project.id}/hooks'
    resp = requests.get(url, headers={'PRIVATE-TOKEN': token}, timeout=2)

    if resp.status_code == 200:
        return resp.json() # always return an iterable

    logger.error(f"Cannot get hooks for {project.full_name}: " + resp.reason)
    return []


def is_webhook_installed(project, jenkins_url=settings.JENKINS_URL):
    hooks = get_webhooks(project)
    jenkins_hook_url = jenkins_url + '/project/' + project.full_name

    for hook in hooks:
        hook_id = hook['id']
        hook_url = hook['url']
        hook_project_id = hook['project_id']
        logger.debug(f"{hook_url}:{jenkins_hook_url} {hook_project_id}:{project.id}")

        if hook_url == jenkins_hook_url and hook_project_id == project.id:
            logger.info(f"hook already installed for {project.full_name}")
            return hook

    logger.info(f"hook not installed for {project.full_name}")
    return False

def delete_webhook(project, hook, token=settings.GITLAB_PRIVATE_TOKEN):
    gitlab_url = '/'.join(project.git_http_url.split('/')[:3])
    hook_id = hook['id']
    url = f'{gitlab_url}/api/v4/projects/{project.id}/hooks/{hook_id}'
    resp = requests.delete(url, headers={'PRIVATE-TOKEN': token}, timeout=2)

    if resp.status_code != 204:
        logger.error(f"Cannot delete hook {hook_id} for {project.full_name}")
        return  False

    logger.info(f"Delete hook {hook_id} for {project.full_name}")
    return True


def install_webhook(
    project,
    token=settings.GITLAB_PRIVATE_TOKEN,
    jenkins_url=settings.JENKINS_URL,
    ssl=settings.GITLAB_JENKINS_TRIGGER_SSL,
    ):
    hook = is_webhook_installed(project)
    if hook:
        if not delete_webhook(project, hook):
            return f'Cannot delete webhook for {project.full_name}' 

    data = {
        "id": project.id,
        "url": jenkins_url + '/project/' + project.full_name,
        "push_events": False,
        "tag_push_events": True,
        "token": project.trigger_token,
        "enable_ssl_verification": ssl,
    }

    gitlab_url = '/'.join(project.git_http_url.split('/')[:3])
    url = f'{gitlab_url}/api/v4/projects/{project.id}/hooks'

    resp = requests.post(url, headers={'PRIVATE-TOKEN': token}, json=data)

    if resp.status_code == 201:
        logger.info(f"New hook installed for {project.full_name}")
        return f'Install GitLab webhook for {project.full_name}' 

    logger.error(f"Cannot install hook for {project.full_name}: " + resp.reason)
    return f'Cannot install GitLab webhook for {project.full_name}'


def get_raw_gitlab_jenkinsfile_url(project):
    gitlab_url = ('/').join(project.git_http_url.split('/')[:3])
    return f'{gitlab_url}/api/v4/projects/{project.id}/repository/files/Jenkinsfile/raw?ref=master'


def get_jenkinsfile(project, token=settings.GITLAB_PRIVATE_TOKEN):
    api_url = get_raw_gitlab_jenkinsfile_url(project)
    resp = requests.get(api_url, headers={'PRIVATE-TOKEN': token}, timeout=2)

    if resp.status_code == 200:
        return resp.text
    else:
        logger.info(f'Cannot read Jenkinsfile for {project.full_name}: ' + str(resp.reason))
        return None