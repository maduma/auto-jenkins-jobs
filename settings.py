import os
import logging

logging.basicConfig()
log_level = logging.getLogger('gunicorn.error').level
if not log_level: # not running gunicorn:
    log_level = logging.DEBUG

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

def obfuscate(secret):
    if len(secret) > 6:
        return secret[:2] + '..' + secret[-2:]
    return 'to_short_to_obfuscate'

logger = get_logger(__name__)

AUTOJJ_VERSION = os.environ.get('AUTOJJ_VERSION','unknown')
GITLAB_URL = os.environ.get('GITLAB_URL','unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
GITLAB_JENKINS_TRIGGER_SECRET = os.environ.get('GITLAB_JENKINS_TRIGGER_SECRET', 'unknown')
GITLAB_JENKINS_TRIGGER_SSL = os.environ.get('GITLAB_JENKINS_TRIGGER_SSL', "TRUE") == "TRUE"
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
JENKINS_GITLAB_CREDS_ID = os.environ.get('JENKINS_GITLAB_CREDS_ID', 'unknown')
JENKINS_ENCRYPTED_SECRET_TOKEN = os.environ.get('JENKINS_ENCRYPTED_SECRET_TOKEN', 'unknown')

PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')

logger.debug(AUTOJJ_VERSION)
logger.debug(GITLAB_URL)
logger.debug(obfuscate(GITLAB_PRIVATE_TOKEN))
logger.debug(obfuscate(GITLAB_JENKINS_TRIGGER_SECRET))
logger.debug(GITLAB_JENKINS_TRIGGER_SSL)
logger.debug(JENKINS_URL)
logger.debug(obfuscate(JENKINS_USERNAME))
logger.debug(obfuscate(JENKINS_PASSWORD))
logger.debug(obfuscate(JENKINS_GITLAB_CREDS_ID))
logger.debug(obfuscate(JENKINS_ENCRYPTED_SECRET_TOKEN))
logger.debug(PROJECT_TYPES)
