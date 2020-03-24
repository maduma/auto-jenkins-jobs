# handle all jenkins requests
import jenkins
import os
import xml.etree.ElementTree as ET
import re

JENKINS_SERVER = os.environ.get('JENKINS_SERVER', 'unknown')
JENKINS_USERNAME = os.environ.get('JENKINS_USERNAME', 'unknown')
JENKINS_PASSWORD = os.environ.get('JENKINS_PASSWORD', 'unknown')

# need mock to test
def is_jenkins_online():
    try:
        server = jenkins_connect()
        id = server.get_whoami().get('id', None)
        version = server.get_version()
        return {'version': version, 'username': id}
    except:
        return False

def is_pipeline_exists(job_name):
    pattern =  '<flow-definition plugin="workflow-job@'
    return is_job_exists(job_name, pattern)

def is_folder_exists(floder_name):
    pattern = '<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@'
    return is_job_exists(floder_name, pattern)

# need mock to test
def is_job_exists(job_name, xml_pattern):
    server = jenkins_connect()
    if not server.get_job_name(job_name):
        return False
    xml = server.get_job_config(job_name)
    if xml_pattern in xml:
        return xml
    return False

def is_job_up_to_date_xml(jenkins_job_xml, pipeline_type='mulePipeline'):
    job_version = get_job_type_and_version(get_description(jenkins_job_xml))
    with open('templates/' + pipeline_type + '.tmpl.xml') as f:
        template_xml = f.read()
        template_version = get_job_type_and_version(get_description(template_xml))
        print(job_version, template_version)
        if job_version == template_version:
            return True
    return False

def get_description(xml):
    root = ET.fromstring(xml)
    for child in root:
        if child.tag == 'description': break
    else:
        raise(LookupError('Cannot find description'))
    return child.text

def get_job_type_and_version(description):
    if not description:
        return None
    pattern = r'\s?Auto Jenkins Job, (\w+):(\S+)'
    match = re.search(pattern, description)
    if match:
        return {'type': match[1], 'version': match[2]}
    return None

def create_xml():
    pass

# need mock to test
def jenkins_connect():
    return jenkins.Jenkins(JENKINS_SERVER, username=JENKINS_USERNAME, password=JENKINS_PASSWORD, timeout=2)

# need mock to test
def create_job(job_name, job_xml):
    server = jenkins_connect()
    pass

# need mock to test
def update_job(job_name, job_xml):
    server = jenkins_connect()
    pass

# need mock to test
def create_folder(flolder_name, folder_xml):
    create_job(folder_name, folder_xml)
    pass