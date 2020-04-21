import os
import logging

gunicorn_log_level = logging.getLogger('gunicorn.error').level
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(gunicorn_log_level)

AUTOJJ_VERSION = '__VERSION__'
GITLAB_URL = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

logger.debug(AUTOJJ_VERSION)
logger.debug(GITLAB_PRIVATE_TOKEN)
logger.debug(JENKINS_URL)
logger.debug(JENKINS_USERNAME)
logger.debug(JENKINS_PASSWORD)
logger.debug(PROJECT_TYPES)