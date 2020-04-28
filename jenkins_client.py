# handle all jenkins requests
import jenkins
import xml.etree.ElementTree as ET
import re
import settings
import collections

logger = settings.get_logger(__name__)

PipelineState = collections.namedtuple('PipelineState', 'is_folder_exists, is_pipeline_exists is_folder_updated is_pipeline_updated', defaults=[True] * 4)

def is_jenkins_online():
    try:
        server = jenkins_connect() # no request done to jenkins server
        server.get_whoami()        # will actually do the request to the server
        return {'status': 'online'}
    except Exception as e:
        logger.error(f'Cannot connecto to Jenkins: {str(e)}')
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
        logger.debug(f'job {name} do not exists')
        return False
    xml = server.get_job_config(name)
    if xml_pattern in xml:
        logger.debug(f'Cannot parse job type for {name}, cannot found - {xml_pattern} -')
        return True
    return False

def is_folder_updated(folder):
    return is_job_xml_updated(folder, template='templates/folder.tmpl.xml')

def is_pipeline_updated(pipeline):
    return is_job_xml_updated(pipeline, template='templates/pipeline.tmpl.xml')

def is_job_xml_updated(name, template):
    server = jenkins_connect()
    job_xml = server.get_job_config(name)
    job_version = get_version(job_xml)
    with open(template) as f:
        template_xml = f.read()
    template_version = get_version(template_xml)
    return template_version == job_version

def get_version(xml):
    description = get_description(xml)
    return parse_description(description)

def get_description(xml):
    root = ET.fromstring(xml)
    for child in root:
        if child.tag == 'description': break
    else:
        raise(LookupError('Cannot find description in job xml'))
    return child.text

def parse_description(description):
    if not description:
        logger.debug('description is empty')
        return None
    pattern = r'\s?Auto Jenkins Job, (\w+):(\S+)'
    match = re.search(pattern, description)
    if match:
        version_type = match[1]
        version = match[2]
        logger.debug(f'autojj description found: {version_type}, {version}')
        return {'type': version_type, 'version': version}
    return None

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

    state = PipelineState(
        is_folder_exists=folder_exists,
        is_folder_updated=folder_updated,
        is_pipeline_exists=pipeline_exists,
        is_pipeline_updated=pipeline_updated
    )
    logger.debug(project)
    logger.debug(state)
    return state

def create_pipeline_xml(
    project,
    template='templates/pipeline.tmpl.xml',
    gitlab_creds_id=settings.JENKINS_GITLAB_CREDS_ID,
    ):
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
    return server

def create_pipeline(project):
    xml = create_pipeline_xml(project)
    server = jenkins_connect()
    server.create_job(project.full_name, xml)
    msg = f'create pipeline {project.full_name}'
    logger.info(msg)
    return msg

def update_pipeline(project):
    msg = f'dummy update pipeline {project.full_name}'
    logger.info(msg)
    return msg

def create_folder(project, template='templates/folder.tmpl.xml'):
    with open(template) as f:
        xml = f.read()
    server = jenkins_connect()
    server.create_job(project.folder, xml)
    msg = f'create folder {project.folder}'
    logger.info(msg)
    return msg

def update_folder(project):
    msg = f'dummy update folder {project.folder}'
    logger.info(msg)
    return msg