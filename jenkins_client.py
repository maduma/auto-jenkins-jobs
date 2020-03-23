# handle all jenkins requests
import jenkins
import os
import xml.etree.ElementTree as ET
import re

JENKINS_SERVER = os.environ.get('JENKINS_SERVER', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')

def is_jenkins_online():
    try:
        server = jenkins_connect()
        id = server.get_whoami().get('id', None)
        version = server.get_version()
        return {'version': version, 'username': id}
    except:
        return False

def is_pipeline_exists(jenkins_pipeline):
    pattern =  '<flow-definition plugin="workflow-job@'
    return is_job_exists(jenkins_pipeline, pattern)

def is_folder_exists(jenkins_folder):
    pattern = '<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@'
    return is_job_exists(jenkins_folder, pattern)

def is_job_exists(jenkins_job, xml_pattern):
    server = jenkins_connect()
    if not server.get_job_name(jenkins_job):
        return False
    xml = server.get_job_config(jenkins_job)
    if xml_pattern in xml:
        return xml
    return False

def is_job_up_to_date(jenkins_job_xml, pipeline_type='mulePipeline'):
    # check the template version
    pass

def get_description(xml):
    root = ET.fromstring(xml)
    for child in root:
        if child.tag == 'description': break
    return child.text

def get_job_type_and_version(description):
    pattern = r'\s?Auto Jenkins Job, (\w+):(\S+)'
    match = re.search(pattern, description)
    if match:
        return {'type': match[1], 'version': match[2]}
    return None

def jenkins_connect():
    return jenkins.Jenkins(JENKINS_SERVER, username=JENKINS_USERNAME, password=JENKINS_PASSWORD, timeout=2)