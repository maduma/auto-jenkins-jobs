from autojj import next_action, NOP, CREATE_FOLDER, CREATE_JOB, UPDATE_JOB, GO_ON, ACTION 
from autojj import get_job, is_autojj_project, get_raw_gitlab_jenkinsfile_url
import json

def test_new_job_creation_folder():
    rest_api = next_action(job_exists=False, folder_exists=False)
    assert rest_api == { ACTION: CREATE_FOLDER, GO_ON: True }
    rest_api = next_action(job_exists=False, folder_exists=False, job_up_to_date=True)
    assert rest_api == { ACTION: CREATE_FOLDER, GO_ON: True }

def test_new_job_creation_job():
    rest_api = next_action(job_exists=False, folder_exists=True)
    assert rest_api == { ACTION: CREATE_JOB, GO_ON: False }
    rest_api = next_action(job_exists=False, folder_exists=True, job_up_to_date=True)
    assert rest_api == { ACTION: CREATE_JOB, GO_ON: False }

def test_update_job():
    rest_api = next_action(job_exists=True, folder_exists=True, job_up_to_date=False)
    assert rest_api == { ACTION: UPDATE_JOB, GO_ON: False }

def test_job_fine():
    rest_api = next_action(job_exists=True, folder_exists=True, job_up_to_date=True)
    assert rest_api == { ACTION: NOP, GO_ON: False }

def test_bad_input1(): # job exists but not the folder !
    rest_api = next_action(job_exists=True, folder_exists=False)
    assert rest_api == { ACTION: NOP, GO_ON: False }
    rest_api = next_action(job_exists=True, folder_exists=False, job_up_to_date=True)
    assert rest_api == { ACTION: NOP, GO_ON: False }

def test_get_job_repository_update_event():
    with open('repository_update_event.json', 'r') as f:
        post_data = json.load(f)
        job = get_job(post_data)
        assert job == { "name": "maduma/toto", "git_url": "https://gitlab.maduma.org/maduma/toto.git" }

def test_get_job__other_event():
    with open('project_destroy_event.json', 'r') as f:
        post_data = json.load(f)
        job = get_job(post_data)
        assert job == None

def test_get_job_bad_data():
    with open('bad_data.json', 'r') as f:
        post_data = json.load(f)
        job = get_job(post_data)
        assert job == None

def test_get_job_no_data():
    job = get_job(None)
    assert job == None

def test_isAutoJJProject_mule_project1():
    jenkinsfile="""
def someveryothercoder = "please"
mulePipeline([
    registry: "cicdships.azurecr.io",
])
"""
    assert is_autojj_project(jenkinsfile, methods=['mulePipeline'])

def test_isAutoJJProject_mule_project2():
    jenkinsfile="""
    mulePipeline registry: "cicdships.azurecr.io"
"""
    assert is_autojj_project(jenkinsfile, methods=[
        'phpPipeline',
        'mulePipeline',
    ])

def test_isAutoJJProject_mule_project_3():
    jenkinsfile="""
    mulePipeline()
"""
    assert is_autojj_project(jenkinsfile, methods=['mulePipeline'])

def test_isAutoJJProject_mule_project_4():
    jenkinsfile="""
    phpPipeline()
"""
    assert is_autojj_project(jenkinsfile, methods=['phpPipeline'])

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
    git_http = 'https://gitlab.maduma.org/maduma/pompiste.git'
    url = get_raw_gitlab_jenkinsfile_url(git_http)
    assert url == 'https://gitlab.maduma.org/maduma/pompiste/-/raw/master/Jenkinsfile'