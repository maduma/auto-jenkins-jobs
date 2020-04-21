import os
import logging

logging.basicConfig(level=logging.INFO)

AUTOJJ_VERSION = '__VERSION__'
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

logging.info(AUTOJJ_VERSION)
logging.info(GITLAB_PRIVATE_TOKEN)
logging.info(JENKINS_URL)
logging.info(JENKINS_USERNAME)
logging.info(JENKINS_PASSWORD)
logging.info(PROJECT_TYPES)
