from autojj import next_action, NOP, CREATE_FOLDER, CREATE_JOB, UPDATE_JOB, GO_ON, ACTION 
from autojj import get_job
import json

def test_new_job_creation_folder():
    rest_api = next_action(job_exists=False, folder_exists=False)
    assert rest_api == { ACTION: CREATE_FOLDER, GO_ON: True }

def test_new_job_creation_job():
    rest_api = next_action(job_exists=False, folder_exists=True)
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