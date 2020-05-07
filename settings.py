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


# requirerd - start
GITLAB_URL = os.environ.get('GITLAB_URL','unknown')
GITLAB_PRIVATE_TOKEN = os.environ.get('GITLAB_PRIVATE_TOKEN','unknown')
JENKINS_URL = os.environ.get('JENKINS_URL', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')
JENKINS_GITLAB_CREDS_ID = os.environ.get('JENKINS_GITLAB_CREDS_ID', 'unknown')
# requirerd - end


AUTOJJ_VERSION = os.environ.get('AUTOJJ_VERSION','__VERSION__')
PROJECT_TYPES = os.environ.get('PROJECT_TYPES', 'mulePipeline').split(',')
GITLAB_JENKINS_TRIGGER_SSL = os.environ.get('GITLAB_JENKINS_TRIGGER_SSL', "TRUE") == "TRUE"


logger.info(f'Version: {AUTOJJ_VERSION}')

logger.debug(GITLAB_URL)
logger.debug(obfuscate(GITLAB_PRIVATE_TOKEN))
logger.debug(GITLAB_JENKINS_TRIGGER_SSL)
logger.debug(JENKINS_URL)
logger.debug(obfuscate(JENKINS_USERNAME))
logger.debug(obfuscate(JENKINS_PASSWORD))
logger.debug(obfuscate(JENKINS_GITLAB_CREDS_ID))
logger.debug(PROJECT_TYPES)
