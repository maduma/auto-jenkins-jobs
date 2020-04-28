from gitlab_client import is_webhook_installed, get_webhooks, install_webhook
from gitlab_client import is_gitlab_online, get_raw_gitlab_jenkinsfile_url, get_jenkinsfile
from autojj import Project
import responses
import json
import gitlab_client
import requests

@responses.activate
def test_get_webhooks():
    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
    )
    responses.add(responses.GET, 'https://gitlab.maduma.org/api/v4/projects/7/hooks', json={"status": "pass"})
    assert get_webhooks(project, token='thisisatoken') == {"status": "pass"}
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'thisisatoken'

def test_is_webhook_installed(monkeypatch):

    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
        full_name = 'maduma/pompiste', folder = '', short_name = '', pipeline = '',
    )
    hooks = [
        {'url': 'https://jenkins.maduma.org/project/web/dentiste', "project_id": 3},
        {'url': 'https://jenkins.maduma.org/project/maduma/pompiste', "project_id": 7},
    ]
    monkeypatch.setattr(gitlab_client, "get_webhooks", lambda project: hooks)
    assert is_webhook_installed(project, jenkins_url='https://jenkins.maduma.org')
    hooks = [
        {'url': 'https://jenkins.maduma.org/project/web/dentiste', "project_id": 4},
        {'url': 'https://jenkins.maduma.org/project/maduma/fleuriste', "project_id": 6},
    ]
    monkeypatch.setattr(gitlab_client, "get_webhooks", lambda project: hooks)
    assert not is_webhook_installed(project, jenkins_url='https://jenkins.maduma.org')

    monkeypatch.setattr(gitlab_client, "get_webhooks", lambda project: [])
    assert not is_webhook_installed(project, jenkins_url='https://jenkins.maduma.org')

@responses.activate
def test_install_webhook_1(monkeypatch):
    monkeypatch.setattr(gitlab_client, "is_webhook_installed", lambda project: False)
    responses.add(responses.POST, 'https://gitlab.maduma.org/api/v4/projects/7/hooks', status=201)
    project = Project(
        id = 7,
        git_http_url = 'https://gitlab.maduma.org/maduma/pompiste.git',
        full_name = 'maduma/pompiste',
    )
    assert install_webhook(project, token='thisisatoken', jenkins_url='https://jenkins.maduma.org',
        jenkins_gitlab_trigger_secret='gitlab_trigger_token')
    assert json.loads(responses.calls[0].request.body.decode('utf-8')) == {
        'id': 7,
        'url': 'https://jenkins.maduma.org/project/maduma/pompiste',
        'push_events': False,
        'tag_push_events': True,
        'token': 'gitlab_trigger_token',
        }

def test_install_web_hook2(monkeypatch):
    monkeypatch.setattr(gitlab_client, "is_webhook_installed", lambda project: True)
    project = Project(full_name = 'maduma/pompiste')
    msg = 'GitLab webhook already installed for maduma/pompiste'
    assert install_webhook(project, token='thisisatoken', jenkins_url='https://jenkins.maduma.org') == msg

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

@responses.activate
def test_is_gitlab_online_1():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/user',
        json={'is_admin': True},
        status=200,
        )
    status = is_gitlab_online(gitlab_url='https://gitlab.maduma.org', token='myprivatetoken')
    assert status == {'status': 'online'}
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'myprivatetoken'

@responses.activate
def test_is_gitlab_online_2():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/user',
        json={'is_admin': False},
        status=200,
        )
    status = is_gitlab_online(gitlab_url='https://gitlab.maduma.org', token='myprivatetoken')
    assert status == {'status': 'degraded', 'message': 'requires higher privileges than provided'}
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'myprivatetoken'

@responses.activate
def test_is_gitlab_online_3():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/user',
        status=500,
        )
    status = is_gitlab_online(gitlab_url='https://gitlab.maduma.org', token='myprivatetoken')
    assert status == {'message': 'Internal Server Error', 'status': 'error'} 
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'myprivatetoken'

def test_is_gitlab_online_4(monkeypatch):
    def raise_exp(url, headers, timeout):
        raise Exception('TEST')
    monkeypatch.setattr(requests, 'get', raise_exp)
    status = is_gitlab_online(gitlab_url='https://gitlab.maduma.org', token='myprivatetoken')
    assert status == {'message': 'TEST', 'status': 'error'} 
