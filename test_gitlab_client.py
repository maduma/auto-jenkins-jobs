from gitlab_client import is_hook_exists, get_all_hooks, install_web_hook, get_raw_gitlab_jenkinsfile_url, get_jenkinsfile
from autojj import Project
import responses
import json
import gitlab_client

@responses.activate
def test_get_all_hooks():
    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
        full_name = '', folder = '', short_name = '', pipeline = '',
    )
    responses.add(responses.GET, 'https://gitlab.maduma.org/api/v4/projects/7/hooks', json={"status": "pass"})
    assert get_all_hooks(project, token='thisisatoken') == {"status": "pass"}
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'thisisatoken'

def test_is_hook_exists():

    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
        full_name = 'maduma/pompiste', folder = '', short_name = '', pipeline = '',
    )
    hooks = [
        {'url': 'https://jenkins.maduma.org/project/web/dentiste', "project_id": 3},
        {'url': 'https://jenkins.maduma.org/project/maduma/pompiste', "project_id": 7},
    ]
    assert is_hook_exists(hooks, project, jenkins_url='https://jenkins.maduma.org')
    hooks = [
        {'url': 'https://jenkins.maduma.org/project/web/dentiste', "project_id": 4},
        {'url': 'https://jenkins.maduma.org/project/maduma/fleuriste', "project_id": 6},
    ]
    assert not is_hook_exists(hooks, project, jenkins_url='https://jenkins.maduma.org')

    hooks = None 
    assert not is_hook_exists(hooks, project, jenkins_url='https://jenkins.maduma.org')

@responses.activate
def test_install_web_hook_1(monkeypatch):
    monkeypatch.setattr(gitlab_client, "is_hook_installed", lambda project: False)
    responses.add(responses.POST, 'https://gitlab.maduma.org/api/v4/projects/7/hooks', status=201)
    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
        full_name = 'maduma/pompiste',
    )
    assert install_web_hook(project, token='thisisatoken', jenkins_url='https://jenkins.maduma.org')
    assert json.loads(responses.calls[0].request.body.decode('utf-8')) == {
        'id': 7,
        'url': 'https://jenkins.maduma.org/project/maduma/pompiste',
        'push_events': True,
        'tag_push_events': True,
        }

def test_install_web_hook_2(monkeypatch):
    monkeypatch.setattr(gitlab_client, "is_hook_installed", lambda project: True)
    project = Project(full_name = 'maduma/pompiste')
    msg = 'GitLab webhook already installed for maduma/pompiste'
    assert install_web_hook(project, token='thisisatoken', jenkins_url='https://jenkins.maduma.org') == msg

@responses.activate
def test_getjenkinsfile():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master',
        body='mulePipeline()',
        status=200,
        )
    project = Project(
        id = 6,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
    )
    jenkinsfile = get_jenkinsfile(project, token="myprivatetoken") 
    assert jenkinsfile == 'mulePipeline()'
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'myprivatetoken'

def test_get_raw_jenkinsfile_url():
    project = Project(
        id = 6,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
    )
    url = get_raw_gitlab_jenkinsfile_url(project)
    assert url == 'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master'