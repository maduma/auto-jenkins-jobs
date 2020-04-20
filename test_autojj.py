from autojj import next_action, NOP, CREATE_FOLDER, CREATE_JOB, UPDATE_JOB, GO_ON, ACTION 
from autojj import parse_event, is_autojj_project, get_raw_gitlab_jenkinsfile_url
from autojj import get_jenkinsfile, actions, is_repository_update, Project
from autojj import process_event
import json
import responses
import autojj

def test_action_new_job_creation_folder():
    rest_api = next_action(job_exists=False, folder_exists=False)
    assert rest_api == { ACTION: CREATE_FOLDER, GO_ON: True }
    rest_api = next_action(job_exists=False, folder_exists=False, job_up_to_date=True)
    assert rest_api == { ACTION: CREATE_FOLDER, GO_ON: True }

def test_action_new_job_creation_job():
    rest_api = next_action(job_exists=False, folder_exists=True)
    assert rest_api == { ACTION: CREATE_JOB, GO_ON: False }
    rest_api = next_action(job_exists=False, folder_exists=True, job_up_to_date=True)
    assert rest_api == { ACTION: CREATE_JOB, GO_ON: False }

def test_action_update_job():
    rest_api = next_action(job_exists=True, folder_exists=True, job_up_to_date=False)
    assert rest_api == { ACTION: UPDATE_JOB, GO_ON: False }

def test_action_job_fine():
    rest_api = next_action(job_exists=True, folder_exists=True, job_up_to_date=True)
    assert rest_api == { ACTION: NOP, GO_ON: False }

def test_action_bad_input(): # job exists but not the folder !
    rest_api = next_action(job_exists=True, folder_exists=False)
    assert rest_api == { ACTION: NOP, GO_ON: False }
    rest_api = next_action(job_exists=True, folder_exists=False, job_up_to_date=True)
    assert rest_api == { ACTION: NOP, GO_ON: False }

def test_parse_event(monkeypatch):
    monkeypatch.setattr(autojj, 'get_jenkinsfile', lambda x, y: 'mulePipeline()')
    with open('test_repository_update_event.json', 'r') as f:
        post_data = json.load(f)
        job = parse_event(post_data)
        assert job == Project(
            id = 6,
            short_name = 'toto',
            full_name='maduma/toto',
            folder = 'maduma',
            git_http_url = "https://gitlab.maduma.org/maduma/toto.git",
            pipeline = 'mulePipeline',
        )

def test_isAutoJJProject_mule_project1():
    jenkinsfile="""
def someveryothercoder = "please"
mulePipeline([
    registry: "cicdships.azurecr.io",
])
"""
    assert is_autojj_project(jenkinsfile, types=['mulePipeline']) == 'mulePipeline'

def test_isAutoJJProject_mule_project2():
    jenkinsfile="""
    mulePipeline registry: "cicdships.azurecr.io"
"""
    assert is_autojj_project(jenkinsfile, types=[
        'phpPipeline',
        'mulePipeline',
    ]) == 'mulePipeline'

def test_isAutoJJProject_mule_project_3():
    jenkinsfile="""
    mulePipeline()
"""
    assert is_autojj_project(jenkinsfile, types=['mulePipeline']) == 'mulePipeline'

def test_isAutoJJProject_mule_project_4():
    jenkinsfile="""
    phpPipeline()
"""
    assert is_autojj_project(jenkinsfile, types=['phpPipeline']) == 'phpPipeline'

def test_isAutoJJProject_mule_project_bad1():
    jenkinsfile="""
examulePipelinetrop([
    registry: "cicdships.azurecr.io",
])
"""
    assert not is_autojj_project(jenkinsfile, types=['phpPipeline'])

def test_isAutoJJProject_mule_project_bad2():
    jenkinsfile="""
    pipeline()
"""
    # check that method are correct (only alphanumeric char)
    assert not is_autojj_project(jenkinsfile, types=['pipeline-2'])

def test_isAutoJJProject_bad3():
    jenkinsfile=None
    assert not is_autojj_project(jenkinsfile, types=['otherPipeline'])

def test_isAutoJJProject_bad4():
    jenkinsfile=''
    assert not is_autojj_project(jenkinsfile, types=['otherPipeline'])

def test_get_raw_jenkinsfile_url():
    project_id = 6
    project_url = 'https://gitlab.maduma.org/maduma/pompiste.git'
    url = get_raw_gitlab_jenkinsfile_url(project_id, project_url)
    assert url == 'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master'

@responses.activate
def test_getjenkinsfile():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master',
        body='mulePipeline()',
        status=200,
        )
    api_url = 'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master'
    jenkinsfile = get_jenkinsfile(api_url, token="myprivatetoken") 
    assert jenkinsfile == 'mulePipeline()'
    assert responses.calls[0].request.headers['PRIVATE-TOKEN'] == 'myprivatetoken'

def mock_get_job_state(states):
    indice = 0
    def get_job_state(project):
        nonlocal indice
        indice = indice + 1
        return states[indice - 1]

    return get_job_state

def test_actions_1(monkeypatch):
    states = [
        (False, False, False),
        (False, True, False),
        (True, True, True),
    ]
    monkeypatch.setattr(autojj, "get_job_state", mock_get_job_state(states))

    all_actions = list(actions(project={}))
    assert all_actions == [
        {ACTION: CREATE_FOLDER, GO_ON: True},
        {ACTION: CREATE_JOB, GO_ON: False},
    ]

def test_actions_2(monkeypatch):
    states = [
        (False, True, False),
        (True, True, True),
    ]
    monkeypatch.setattr(autojj, "get_job_state", mock_get_job_state(states))

    all_actions = list(actions(project={}))
    assert all_actions == [
        {ACTION: CREATE_JOB, GO_ON: False},
    ]

def test_actions_3(monkeypatch):
    states = [
        (True, True, False),
        (True, True, True),
    ]
    monkeypatch.setattr(autojj, "get_job_state", mock_get_job_state(states))

    all_actions = list(actions(project={}))
    assert all_actions == [
        {ACTION: UPDATE_JOB, GO_ON: False},
    ]

def test_is_repository_update_event():
    assert is_repository_update({}) == False
    assert is_repository_update("hello") == False
    assert is_repository_update([1, 2, "hello"]) == False
    assert is_repository_update([]) == False
    assert is_repository_update(None) == False
    assert is_repository_update({'event_name': 'project_creation'}) == False
    assert is_repository_update({'event_name': 'repository_update'}) == True

def test_process_event_not_repo_update():
    event = {'event_name': 'test_event'}
    assert process_event(event) == ("Can only handle GitLab 'repository_update' event", 400)

def test_process_event_no_pipeline(monkeypatch):
    project = Project(
        id = 0, full_name = '', folder = '', short_name = '', git_http_url = '',
        pipeline = False,
    )
    monkeypatch.setattr(autojj, "parse_event", lambda x: project)
    assert process_event({'event_name': 'repository_update'}) == ("Unknown Jenkins Pipeline", 200)

def test_process_event(monkeypatch):
    project = Project(
        id = 0, full_name = '', folder = '', short_name = '', git_http_url = '',
        pipeline = 'phpPipeline',
    )
    monkeypatch.setattr(autojj, "parse_event", lambda x: project)
    monkeypatch.setattr(autojj, "do_jenkins_actions", lambda x: 'ACTIONS_DONE')
    assert process_event({'event_name': 'repository_update'}) == ("Event processed: ACTIONS_DONE", 200)