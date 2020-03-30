from autojj import next_action, NOP, CREATE_FOLDER, CREATE_JOB, UPDATE_JOB, GO_ON, ACTION 
from autojj import get_project, is_autojj_project, get_raw_gitlab_jenkinsfile_url
from autojj import get_jenkinsfile, actions
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

def test_get_project_repository_update_event():
    with open('test_repository_update_event.json', 'r') as f:
        post_data = json.load(f)
        job = get_project(post_data)
        assert job == { "id": 6, "name": "maduma/toto", "git_url": "https://gitlab.maduma.org/maduma/toto.git" , "namespace": "maduma", "short_name": "toto"}

def test_get_project_other_event():
    with open('test_project_destroy_event.json', 'r') as f:
        post_data = json.load(f)
        job = get_project(post_data)
        assert job == None

def test_get_project_bad_data():
    with open('test_bad_data.json', 'r') as f:
        post_data = json.load(f)
        job = get_project(post_data)
        assert job == None

def test_get_project_no_data():
    job = get_project(None)
    assert job == None

def test_isAutoJJProject_mule_project1():
    jenkinsfile="""
def someveryothercoder = "please"
mulePipeline([
    registry: "cicdships.azurecr.io",
])
"""
    assert is_autojj_project(jenkinsfile, methods=['mulePipeline']) == 'mulePipeline'

def test_isAutoJJProject_mule_project2():
    jenkinsfile="""
    mulePipeline registry: "cicdships.azurecr.io"
"""
    assert is_autojj_project(jenkinsfile, methods=[
        'phpPipeline',
        'mulePipeline',
    ]) == 'mulePipeline'

def test_isAutoJJProject_mule_project_3():
    jenkinsfile="""
    mulePipeline()
"""
    assert is_autojj_project(jenkinsfile, methods=['mulePipeline']) == 'mulePipeline'

def test_isAutoJJProject_mule_project_4():
    jenkinsfile="""
    phpPipeline()
"""
    assert is_autojj_project(jenkinsfile, methods=['phpPipeline']) == 'phpPipeline'

def test_isAutoJJProject_mule_project_bad1():
    jenkinsfile="""
examulePipelinetrop([
    registry: "cicdships.azurecr.io",
])
"""
    assert not is_autojj_project(jenkinsfile, methods=['phpPipeline'])

def test_isAutoJJProject_mule_project_bad2():
    jenkinsfile="""
    pipeline()
"""
    # check that method are correct (only alphanumeric char)
    assert not is_autojj_project(jenkinsfile, methods=['pipeline-2'])

def test_get_raw_jenkinsfile_url():
    project = {'id': 6, 'git_url': 'https://gitlab.maduma.org/maduma/pompiste.git', 'name': 'maduma/pompiste'}
    url = get_raw_gitlab_jenkinsfile_url(project)
    assert url == 'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master'

@responses.activate
def test_getjenkinsfile():
    responses.add(
        responses.GET,
        'https://gitlab.maduma.org/api/v4/projects/6/repository/files/Jenkinsfile/raw?ref=master',
        body='mulePipeline()',
        status=200,
        )
    project = {'id': 6, 'git_url': 'https://gitlab.maduma.org/maduma/pompiste.git', 'name': 'maduma/pompiste'}
    jenkinsfile = get_jenkinsfile(project, token="myprivatetoken") 
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