import os
import requests

import logging

logging.basicConfig(level=logging.INFO)

JENKINS_URL = os.environ.get('JENKINS_SERVER', 'https://jenkins.maduma.org')
GITLAB_TOKEN = os.environ.get('GIT_PRIVATE_TOKEN','unknown')

def get_all_hooks(project, token=GITLAB_TOKEN):
    project_id = project['id']
    headers = {'PRIVATE-TOKEN': token}
    url = '{gitlab_url}/api/v4/projects/{project_id}/hooks'.format(
        gitlab_url = '/'.join(project['git_url'].split('/')[:3]),
        project_id = project_id,
    )
    resp = requests.get(url, headers=headers, timeout=2)
    if resp.status_code == 200:
        return resp.json()
    logging.error("Cannot get all hooks: " + resp.reason)
    logging.error("url: {url}, token: {token}".format(url=url, token=token))
    return None

def is_hook_exists(hooks, project, jenkins_url=JENKINS_URL):
    if not hooks:
        hooks = []
    jenkins_hook_url = jenkins_url + '/project/' + project['name']
    for hook in hooks:
        if hook['url'] == jenkins_hook_url and hook['id'] == project['id']:
            logging.info("hook already installed")
            return True
    logging.info("hook not already installed")
    return False

def is_hook_installed(project, jenkins_url=JENKINS_URL):
    hooks = get_all_hooks(project, token=GITLAB_TOKEN)
    return is_hook_exists(hooks, project, jenkins_url=JENKINS_URL)

def install_jenkins_hook(project, token=GITLAB_TOKEN, jenkins_url=JENKINS_URL):
    jenkins_hook_url = jenkins_url + '/project/' + project['name']
    data = {
        "id": project['id'],
        "url": jenkins_hook_url,
        "push_events": True,
        "tag_push_events": True
    }
    url = '{gitlab_url}/api/v4/projects/{project_id}/hooks'.format(
        gitlab_url = '/'.join(project['git_url'].split('/')[:3]),
        project_id = project['id'],
    )
    headers = {'PRIVATE-TOKEN': token}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        return True
    return False