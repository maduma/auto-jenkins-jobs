import logging

ACTION = 0
GO_ON = 1

NOP = 0
CREATE_JOB = 1
UPDATE_JOB = 2
CREATE_FOLDER = 3

def next_api(job_exists, folder_exists, job_up_to_date=False):
    if folder_exists:
        if job_exists:
            if job_up_to_date:
                return {ACTION: NOP, GO_ON: False}
            else:
                return {ACTION: UPDATE_JOB, GO_ON: False}
        else:
            return {ACTION: CREATE_JOB, GO_ON: False}
    elif job_exists:
        logging.error(f'Bad input: job_exists={job_exists} but not folder_exists={folder_exists}')
        return {ACTION: NOP, GO_ON: False}
    else:
        return {ACTION: CREATE_FOLDER, GO_ON: True}

    logging.error(f'Bad input: job_exists={job_exists} , folder_exists={folder_exists} , job_up_to_date={job_up_to_date}')
    return {ACTION: NOP, GO_ON: False}