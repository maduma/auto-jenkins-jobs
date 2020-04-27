# handle all jenkins requests
import jenkins
import os
import xml.etree.ElementTree as ET
import re
import logging
import settings
import collections

PipelineState = collections.namedtuple('PipelineState', 'is_folder_exists, is_pipeline_exists is_folder_updated is_pipeline_updated', defaults=[True] * 4)

def is_jenkins_online():
    try:
        server = jenkins_connect()
        server.get_version()
        return {'status': 'online'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def is_pipeline_exists(pipeline):
    pattern =  '<flow-definition plugin="workflow-job@'
    return is_job_exists(pipeline, pattern)

def is_folder_exists(folder):
    pattern = '<com.cloudbees.hudson.plugins.folder.Folder plugin="cloudbees-folder@'
    return is_job_exists(folder, pattern)

def is_job_exists(name, xml_pattern):
    server = jenkins_connect()
    if not server.get_job_name(name):
        return False
    xml = server.get_job_config(name)
    if xml_pattern in xml:
        return True
    return False

def is_folder_updated(folder):
    return is_job_xml_updated(folder, template='templates/folder.tmpl.xml')

def is_pipeline_updated(pipeline):
    return is_job_xml_updated(pipeline, template='templates/pipeline.tmpl.xml')

def is_job_xml_updated(name, template):
    server = jenkins_connect()
    job_xml = server.get_job_config(name)
    job_version = get_job_type_and_version(get_description(job_xml))
    with open(template) as f:
        template_xml = f.read()
    template_version = get_job_type_and_version(get_description(template_xml))
    return template_version == job_version


def get_pipeline_state(project):
    folder_exists = is_folder_exists(project.folder)
    folder_updated = True
    pipeline_exists = False
    pipeline_updated = True

    if folder_exists:
        folder_updated = is_folder_updated(project.folder)
        pipeline_exists = is_pipeline_exists(project.full_name)
        if pipeline_exists:
            pipeline_updated = is_pipeline_updated(project.full_name)

    return PipelineState(
        is_folder_exists=folder_exists,
        is_folder_updated=folder_updated,
        is_pipeline_exists=pipeline_exists,
        is_pipeline_updated=pipeline_updated
    )

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

def create_pipeline_xml(project, template='templates/pipeline.tmpl.xml',
               gitlab_creds_id=settings.JENKINS_GITLAB_CREDS_ID):
    with open(template) as f:
        xml = f.read()
        xml = xml.format(
            job_name=project.short_name,
            git_http_url=project.git_http_url,
            git_creds_id=gitlab_creds_id,
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

def create_pipeline(project):
    logging.info('create pipeline %s' % project.full_name)
    xml = create_pipeline_xml(project)
    server = jenkins_connect()
    server.create_job(project.full_name, xml)

def update_folder(project):
    logging.info('update folder %s' % project.folder)
    pass

def update_pipeline(project):
    logging.info('update folder %s' % project.folder)
    #server.reconfig_job(project.full_name, xml)
    pass

def create_folder(project, template='templates/folder.tmpl.xml'):
    logging.info('create folder %s' % project.folder)
    server = jenkins_connect()
    with open(template) as f:
        xml = f.read()
        server.create_job(project.folder, xml)
