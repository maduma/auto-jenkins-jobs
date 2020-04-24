import os
import requests
import logging
import settings

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
    logging.error("Cannot get hooks: " + resp.reason)
    return []

def is_webhook_installed(project, jenkins_url=settings.JENKINS_URL):
    hooks = get_webhooks(project)
    jenkins_hook_url = jenkins_url + '/project/' + project.full_name

    for hook in hooks:
        hook_url = hook['url']
        hook_project_id = hook['project_id']
        logging.info(f"{hook_url}:{jenkins_hook_url} {hook_project_id}:{project.id}")

        if hook_url == jenkins_hook_url and hook_project_id == project.id:
            logging.info("hook already installed")
            return True

    logging.info("hook not already installed")
    return False

def install_webhook(project, token=settings.GITLAB_PRIVATE_TOKEN, jenkins_url=settings.JENKINS_URL):
    if is_webhook_installed(project):
        return f'GitLab webhook already installed for {project.full_name}' 

    data = {
        "id": project.id,
        "url": jenkins_url + '/project/' + project.full_name,
        "push_events": True,
        "tag_push_events": True
    }
    gitlab_url = '/'.join(project.git_http_url.split('/')[:3])
    url = f'{gitlab_url}/api/v4/projects/{project.id}/hooks'

    resp = requests.post(url, headers={'PRIVATE-TOKEN': token}, json=data)
    if resp.status_code == 201:
        logging.info(f"new hook installed for {project.full_name}")
        return f'Install GitLab webhook for {project.full_name}' 
    logging.error("Cannot install hook: " + resp.reason)
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
        logging.error('Cannot get Jenkins file ' + str(resp.reason))
        return None