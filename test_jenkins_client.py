from jenkins_client import parse_description, get_description
from jenkins_client import create_pipeline_xml, get_pipeline_state, PipelineState, is_job_exists
from jenkins_client import jenkins_connect, create_folder
from jenkins_client import is_folder_exists, is_pipeline_exists, is_jenkins_online, is_job_xml_updated, get_version
from autojj import Project
import jenkins
import responses
import pytest
import test_jenkins_mock
import jenkins_client
import settings

def test_is_jenkins_online_good(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert is_jenkins_online() == {'status': 'online'}

def test_is_jenkins_online_bad_1(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    monkeypatch.setattr(settings, "JENKINS_URL", "BAD")
    assert is_jenkins_online() == {'status': 'error', 'message': 'SERVER_ERROR'}

def test_is_jenkins_online_bad_2(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    monkeypatch.setattr(settings, "JENKINS_PASSWORD", "BAD")
    assert is_jenkins_online() == {'status': 'error', 'message': 'AUTHENTICATION_ERROR'}

def test_is_job_xml_updated_1(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert not is_job_xml_updated('job1', template='test_pipeline.tmpl.xml')

def test_is_job_xml_updated_2(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert not is_job_xml_updated('job2', template='test_pipeline.tmpl.xml')

def test_is_job_xml_updated_3(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert is_job_xml_updated('job3', template='test_pipeline.tmpl.xml')

def test_get_version(monkeypatch):
    assert get_version('<top><description>Auto Jenkins Job, mulePipeline:0.0.2</description></top>') == {'type': 'mulePipeline', 'version': '0.0.2'}

def test_get_description():
    with open('test_job_good.xml', 'r') as f:
        xml = f.read()
        assert get_description(xml) == 'Auto Jenkins Job, mulePipeline:0.0.2'

def test_get_description_bad():
    with pytest.raises(LookupError):
        with open('test_job_bad.xml', 'r') as f:
            xml = f.read()
            get_description(xml)

def test_parse_description_version_1():
    assert parse_description(
        'Auto Jenkins Job, mulePipeline:0.0.2'
        ) == { 'type': 'mulePipeline', 'version': '0.0.2'}

def test_parse_description_version_2():
    assert parse_description(
        'some other stuff before \n again \n blabla Auto Jenkins Job, mulePipeline:0.0.2 and other stuff after'
        ) == { 'type': 'mulePipeline', 'version': '0.0.2'}

def test_parse_description_version_empty():
    assert parse_description(None) == None

def test_create_pipeline_xml():
    project =  Project(id=0, full_name='maduma/dentiste', folder='maduma', short_name='dentiste', pipeline='phpPipeline',
        git_http_url = 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git',
    )
    xml = create_pipeline_xml(project, template='test_pipeline_short.tmpl.xml')
    assert xml == """<gitLabConnection></gitLabConnection>
<name>dentiste</name>
<url>https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git</url>
<credentialsId>unknown</credentialsId>
"""

def test_create_pipeline_xml_default_template():
    project =  Project(id=0, full_name='maduma/dentiste', folder='maduma', short_name='dentiste', pipeline='phpPipeline',
        git_http_url = 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git',
    )
    xml = create_pipeline_xml(project)
    assert xml.startswith('<')

def test_jenkins_connect(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert getattr(jenkins_connect(), 'server_created')

def test_jenkins_create_folder(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    with pytest.raises(test_jenkins_mock.Job_created_exception) as ex:
        create_folder(Project(folder='mule'))
    assert str(ex.value) == 'mule'

def test_is_folder_pipeline_exists(monkeypatch):
    def is_job_exists_mock(name, pattern):
        if not pattern:
            raise Exception('Pattern should not be null')
        return name
    monkeypatch.setattr(jenkins_client, 'is_job_exists', is_job_exists_mock)
    assert is_folder_exists('my_folder') == 'my_folder'
    assert is_pipeline_exists('my_folder') == 'my_folder'

def test_is_job_exists_1(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert is_job_exists('my_job', 'XML')

def test_is_job_exists_2(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert not is_job_exists('NO_JOB', 'XML')

def test_is_job_exists_3(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert not is_job_exists('my_job', 'BAD_PATTERN')

def test_pipeline_state_1(monkeypatch):
    project = Project(full_name="FULL_NAME", folder='FOLDER')
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: folder == 'FOLDER')
    monkeypatch.setattr(jenkins_client, 'is_folder_updated', lambda folder: folder == 'FOLDER')
    monkeypatch.setattr(jenkins_client, 'is_pipeline_exists', lambda pipeline: pipeline == 'FULL_NAME')
    monkeypatch.setattr(jenkins_client, 'is_pipeline_updated', lambda pipeline: pipeline == 'FULL_NAME')
    state = PipelineState()
    assert get_pipeline_state(project) == state
   
def test_pipeline_state_2(monkeypatch):
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: False)
    state = PipelineState(is_folder_exists=False, is_pipeline_exists=False)
    assert get_pipeline_state(Project()) == state

def test_pipeline_state_3(monkeypatch):
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_folder_updated', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_exists', lambda folder: False)
    state = PipelineState(is_folder_exists=True, is_folder_updated=True, is_pipeline_exists=False)
    assert get_pipeline_state(Project()) == state

def test_pipeline_state_4(monkeypatch):
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_folder_updated', lambda folder: False)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_exists', lambda folder: False)
    state = PipelineState(is_folder_exists=True, is_folder_updated=False, is_pipeline_exists=False)
    assert get_pipeline_state(Project()) == state
   
def test_pipeline_state_5(monkeypatch):
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_folder_updated', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_updated', lambda folder: False)
    state = PipelineState(is_folder_exists=True, is_folder_updated=True, is_pipeline_exists=True, is_pipeline_updated=False)
    assert get_pipeline_state(Project()) == state
   
def test_pipeline_state_6(monkeypatch):
    monkeypatch.setattr(jenkins_client, 'is_folder_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_folder_updated', lambda folder: False)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_exists', lambda folder: True)
    monkeypatch.setattr(jenkins_client, 'is_pipeline_updated', lambda folder: True)
    state = PipelineState(is_folder_exists=True, is_folder_updated=False, is_pipeline_exists=True, is_pipeline_updated=True)
    assert get_pipeline_state(Project()) == state
   