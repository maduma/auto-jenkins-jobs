import os

AUTOJJ_VERSION = os.environ.get('AUTOJJ_VERSION', 'unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')