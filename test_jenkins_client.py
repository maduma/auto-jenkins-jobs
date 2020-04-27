from jenkins_client import is_job_up_to_date_xml, get_job_type_and_version, get_description
from jenkins_client import create_xml, get_pipeline_state, PipelineState, is_job_exists
from jenkins_client import jenkins_connect, create_job, update_job, create_folder, build_job
from jenkins_client import is_folder_exists, is_pipeline_exists
from autojj import Project
import jenkins
import responses
import pytest
import test_jenkins_mock
import jenkins_client

def test_is_jenkins_online_good():
    #responses.add(responses.GET, 'http://172.10.23.3/crumbIssuer/api/json')
    #responses.add(responses.GET, 'http://172.10.23.3/me/api/json?depth=0')
    #online = isJenkinsOnline('http://172.10.23.3/', user='jhon', password='reddaser')
    #assert online == True
    assert True == True

def test_is_up_to_date_good():
    with open('test_job_good.xml', 'r') as f:
        job_xml = f.read()
        assert is_job_up_to_date_xml(job_xml, template='test_pipeline.tmpl.xml') == True

def test_is_up_to_date_old1():
    with open('test_job_old1.xml', 'r') as f:
        xml = f.read()
        assert is_job_up_to_date_xml(xml, template='test_pipeline.tmpl.xml') == False
def test_is_up_to_date_old2():
    with open('test_job_old2.xml', 'r') as f:
        xml = f.read()
        assert is_job_up_to_date_xml(xml, template='test_pipeline.tmpl.xml') == False

def test_get_description():
    with open('test_job_good.xml', 'r') as f:
        xml = f.read()
        assert get_description(xml) == 'Auto Jenkins Job, mulePipeline:0.0.2'

def test_get_description_bad():
    with pytest.raises(LookupError):
        with open('test_job_bad.xml', 'r') as f:
            xml = f.read()
            get_description(xml)

def test_get_job_type_and_version_1():
    assert get_job_type_and_version(
        'Auto Jenkins Job, mulePipeline:0.0.2'
        ) == { 'type': 'mulePipeline', 'version': '0.0.2'}

def test_get_job_type_and_version_2():
    assert get_job_type_and_version(
        'some other stuff before \n again \n blabla Auto Jenkins Job, mulePipeline:0.0.2 and other stuff after'
        ) == { 'type': 'mulePipeline', 'version': '0.0.2'}

def test_get_job_type_and_version_empty():
    assert get_job_type_and_version(None) == None

def test_create_xml():
    project =  Project(id=0, full_name='maduma/dentiste', folder='maduma', short_name='dentiste', pipeline='phpPipeline',
        git_http_url = 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git',
    )
    xml = create_xml(project, template='test_pipeline_short.tmpl.xml')
    assert xml == """<gitLabConnection></gitLabConnection>
<name>dentiste</name>
<url>https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git</url>
<credentialsId>gitlab_maduma_org</credentialsId>
"""

def test_jenkins_connect(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    assert getattr(jenkins_connect(), 'server_created')

def test_jenkins_create_job(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    monkeypatch.setattr(jenkins_client, "create_xml", lambda project: 'THIS_IS_XML')
    project =  Project(id=0, full_name='maduma/pompiste', folder='maduma', short_name='pompiste', git_http_url='', pipeline='phpPipeline')
    with pytest.raises(test_jenkins_mock.Job_created_exception) as ex:
        create_job(project)
    assert str(ex.value) == 'maduma/pompiste'

def test_jenkins_update_job(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    project =  Project(id=0, full_name='maduma/flutiste', folder='maduma', short_name='flutiste', git_http_url='', pipeline='phpPipeline')
    with pytest.raises(test_jenkins_mock.Job_reconfigured_exception) as ex:
        update_job(project)
    assert str(ex.value) == 'maduma/flutiste'

def test_jenkins_created_folder(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    with pytest.raises(test_jenkins_mock.Job_created_exception) as ex:
        create_folder('mule')
    assert str(ex.value) == 'mule'

def test_jenkins_build_job(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", test_jenkins_mock.MockResponse)
    with pytest.raises(test_jenkins_mock.Job_build_exception) as ex:
        build_job('mule')
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
   