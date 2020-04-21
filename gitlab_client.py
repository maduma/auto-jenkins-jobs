import os
import requests
import logging
import settings

def is_gitlab_online(gitlab_url=settings.GITLAB_URL, token=settings.GITLAB_PRIVATE_TOKEN):
    pass

def get_all_hooks(project, token=settings.GITLAB_PRIVATE_TOKEN):
    url = '{gitlab_url}/api/v4/projects/{project_id}/hooks'.format(
        gitlab_url = '/'.join(project.git_http_url.split('/')[:3]),
        project_id = project.id,
    )
    resp = requests.get(url, headers={'PRIVATE-TOKEN': token}, timeout=2)
    if resp.status_code == 200:
        return resp.json()
    logging.error("Cannot get all hooks: " + resp.reason)
    return None

def is_hook_exists(hooks, project, jenkins_url=settings.JENKINS_URL):
    if not hooks:
        hooks = []
    jenkins_hook_url = jenkins_url + '/project/' + project.full_name
    for hook in hooks:
        logging.info("{hook_url}:{j_url} {hook_id}:{p_id}".format(
            hook_url = hook['url'],
            j_url = jenkins_hook_url,
            hook_id = hook['project_id'],
            p_id = project.id,
        ))
        if hook['url'] == jenkins_hook_url and hook['project_id'] == project.id:
            logging.info("hook already installed")
            return True
    logging.info("hook not already installed")
    return False

def is_hook_installed(project):
    hooks = get_all_hooks(project)
    return is_hook_exists(hooks, project)

def install_jenkins_hook(project, token=settings.GITLAB_PRIVATE_TOKEN, jenkins_url=settings.JENKINS_URL):
    jenkins_hook_url = jenkins_url + '/project/' + project.full_name
    data = {
        "id": project.id,
        "url": jenkins_hook_url,
        "push_events": True,
        "tag_push_events": True
    }
    url = '{gitlab_url}/api/v4/projects/{project_id}/hooks'.format(
        gitlab_url = '/'.join(project.git_http_url.split('/')[:3]),
        project_id = project.id,
    )
    resp = requests.post(url, headers={'PRIVATE-TOKEN': token}, json=data)
    if resp.status_code == 201:
        logging.info("new hook installed")
        return True
    logging.error("Cannot install hook: " + resp.reason)
    return False