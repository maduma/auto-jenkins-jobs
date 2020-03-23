# handle all jenkins requests
import jenkins
import os

JENKINS_SERVER = os.environ.get('JENKINS_SERVER', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')

def isJenkinsOnline():
    try:
        server = jenkins_connect()
        id = server.get_whoami().get('id', None)
        version = server.get_version()
        return {'version': version, 'username': id}
    except:
        return False

def isPipelineExists(jenkins_pipeline):
    pattern =  '<flow-definition plugin="workflow-job@'
    return isJobExists(jenkins_folder, pattern)

def isFolderExists(jenkins_folder):
    pattern = '<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@'
    return isJobExists(jenkins_folder, pattern)

def isJobExists(jenkins_job, xml_pattern):
    server = jenkins_connect()
    if not server.get_job_name(jenkins_job):
        return False
    xml = server.get_job_config(jenkins_job)
    print(xml)
    if xml_pattern in xml:
        return True
    return False

def jenkins_connect():
    return jenkins.Jenkins(JENKINS_SERVER, username=JENKINS_USERNAME, password=JENKINS_PASSWORD, timeout=2)