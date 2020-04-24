# handle all jenkins requests
import jenkins
import os
import xml.etree.ElementTree as ET
import re
import logging
import settings
import collections

PipelineState = collections.namedtuple('PipelineState', 'is_folder_exists, is_pipeline_exists is_folder_updated is_pipeline_updated', defaults=[True] * 4)

# to test
def is_jenkins_online():
    try:
        server = jenkins_connect()
        server.get_version()
        return {'status': 'online'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def is_pipeline_exists(job_name):
    pattern =  '<flow-definition plugin="workflow-job@'
    return is_job_exists(job_name, pattern)

def is_folder_exists(folder_name):
    pattern = '<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@'
    return is_job_exists(folder_name, pattern)

# need mock to test
def is_job_exists(job_name, xml_pattern):
    server = jenkins_connect()
    if not server.get_job_name(job_name):
        return False
    xml = server.get_job_config(job_name)
    if xml_pattern in xml:
        return xml
    return False

def is_folder_updated(job_name):
    return True

def is_pipeline_updated(job_name):
    return True

def get_pipeline_state(project):
    is_folder_exists = is_folder_exists(project)

    is_folder_updated = True
    if is_folder_exists:
        is_folder_updated = is_folder_updated(project)

    is_pipeline_exists = is_pipeline_exists(project)

    is_pipeline_updated = True
    if is_pipeline_exists:
        is_pipeline_updated = is_pipeline_updated(project)

    return PipelineState(
        is_folder_exists=is_folder_exists,
        is_folder_updated=is_folder_updated,
        is_pipeline_exists=is_pipeline_exists,
        is_pipeline_updated=is_pipeline_updated
    )

def is_job_up_to_date_xml(jenkins_job_xml, template='templates/pipeline.tmpl.xml'):
    job_version = get_job_type_and_version(get_description(jenkins_job_xml))
    with open(template) as f:
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

def create_xml(project, template='templates/pipeline.tmpl.xml'):
    with open(template) as f:
        xml = f.read()
        xml = xml.format(
            job_name=project.short_name,
            git_http_url=project.git_http_url,
            git_creds_id='gitlab_maduma_org',
            gitlab_connection='',
        )
        return xml

def jenkins_connect():
    server =  jenkins.Jenkins(
        settings.JENKINS_URL,
        username=settings.JENKINS_USERNAME,
        password=settings.JENKINS_PASSWORD,
        timeout=2,
        )
    server.get_whoami()
    return server

def create_job(project):
    logging.info('create project %s' % project.full_name)
    xml = create_xml(project)
    server = jenkins_connect()
    server.create_job(project.full_name, xml)

def create_pipeline(project):
    pass

def update_job(project):
    logging.info('update project %s' % project.full_name)
    xml = create_xml(project)
    server = jenkins_connect()
    server.reconfig_job(project.full_name, xml)

def update_folder(project):
    pass

def update_pipeline(project):
    pass

def create_folder(folder_name):
    logging.info('create folder %s' % folder_name)
    server = jenkins_connect()
    with open('templates/folder.xml') as f:
        folder_xml = f.read()
        server.create_job(folder_name, folder_xml)

def build_job(job_name):
    logging.info('build job %s' % job_name)
    server = jenkins_connect()
    server.build_job(job_name, parameters={'DEPLOY_TO': 'tst'})
