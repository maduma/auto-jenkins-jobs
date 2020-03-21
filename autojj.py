import logging

logging.basicConfig(level=logging.DEBUG)

ACTION = 'action'
GO_ON = 'go_on'
NOP = None
CREATE_JOB = 'create_job'
UPDATE_JOB = 'update_job'
CREATE_FOLDER = 'create_folder'

def next_api(job_exists, folder_exists, job_up_to_date=False):
    api = {}

    if folder_exists:
        if job_exists:
            if job_up_to_date:
                api = {ACTION: NOP, GO_ON: False}
            else:
                api = {ACTION: UPDATE_JOB, GO_ON: False}
        else:
            api = {ACTION: CREATE_JOB, GO_ON: False}
    elif job_exists:
        logging.error(f'Bad input: job_exists={job_exists} but not folder. folder_exists={folder_exists}')
        api = {ACTION: NOP, GO_ON: False}
    else:
        api = {ACTION: CREATE_FOLDER, GO_ON: True}

    if not api:
        logging.error(f'Bad input: job_exists={job_exists} , folder_exists={folder_exists} , job_up_to_date={job_up_to_date}')
        api = {ACTION: NOP, GO_ON: False}
    else:
        logging.debug(f'job_exists={job_exists} , folder_exists={folder_exists} , job_up_to_date={job_up_to_date}')
        logging.info(f'ACTION: {api[ACTION]}, GO_ON: {api[GO_ON]}')
    return api