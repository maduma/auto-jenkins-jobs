from autojj import next_action, NOP, CREATE_FOLDER, CREATE_JOB, UPDATE_JOB, GO_ON, ACTION 

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