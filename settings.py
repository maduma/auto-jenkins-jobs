import os
import logging

logging.basicConfig()
log_level = logging.getLogger('gunicorrn.error').level
if not log_level: # not running gunicorn:
    log_level = logging.INFO

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

logger = get_logger(__name__)

AUTOJJ_VERSION = '__VERSION__'
GITLAB_URL = os.environ.get('GITLAB_URL','unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
JENKINS_GITLAB_CREDS_ID = os.environ.get('JENKINS_GITLAB_CREDS_ID', 'unknown')

PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

logger.debug(AUTOJJ_VERSION)
logger.debug(GITLAB_URL)
logger.debug(GITLAB_PRIVATE_TOKEN)
logger.debug(JENKINS_URL)
logger.debug(JENKINS_USERNAME)
logger.debug(JENKINS_PASSWORD)
logger.debug(JENKINS_GITLAB_CREDS_ID)
logger.debug(PROJECT_TYPES)