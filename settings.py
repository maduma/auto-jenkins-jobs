import os

AUTOJJ_VERSION = os.environ.get('AUTOJJ_VERSION', 'unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')

PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

print(JENKINS_URL)
print(JENKINS_USERNAME)
print(JENKINS_PASSWORD)