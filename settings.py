import os
import logging

logging.basicConfig(level=logging.DEBUG)

AUTOJJ_VERSION = os.environ.get('AUTOJJ_VERSION', '__VERSION__')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

logging.debug(JENKINS_URL)
logging.debug(JENKINS_USERNAME)
logging.debug(JENKINS_PASSWORD)