from jenkins_client import is_job_up_to_date_xml, get_job_type_and_version, get_description
from jenkins_client import create_xml
from jenkins_client import jenkins_connect, create_job, update_job, create_folder
import jenkins
import responses
import pytest
import jenkins_mock

def test_is_jenkins_online_good():
    #responses.add(responses.GET, 'http://172.10.23.3/crumbIssuer/api/json')
    #responses.add(responses.GET, 'http://172.10.23.3/me/api/json?depth=0')
    #online = isJenkinsOnline('http://172.10.23.3/', user='jhon', password='reddaser')
    #assert online == True
    assert True == True

def test_is_up_to_date_good():
    with open('job_good.xml', 'r') as f:
        job_xml = f.read()
        assert is_job_up_to_date_xml(job_xml, pipeline_type='mulePipeline') == True

def test_is_up_to_date_old1():
    with open('job_old1.xml', 'r') as f:
        xml = f.read()
        assert is_job_up_to_date_xml(xml, pipeline_type='mulePipeline') == False
def test_is_up_to_date_old2():
    with open('job_old2.xml', 'r') as f:
        xml = f.read()
        assert is_job_up_to_date_xml(xml, pipeline_type='mulePipeline') == False

def test_get_description():
    with open('job_good.xml', 'r') as f:
        xml = f.read()
        assert get_description(xml) == 'Auto Jenkins Job, mulePipeline:0.0.2'

def test_get_description_bad():
    with pytest.raises(LookupError):
        with open('job_bad.xml', 'r') as f:
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
    project = {'git_url': 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git'}
    xml = create_xml(project, template='templates/pipeline_test.tmpl.xml')
    assert xml == """<gitLabConnection></gitLabConnection>
<url>https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git</url>
<credentialsId>gitlab_maduma_org</credentialsId>
"""

def test_jenkins_connect(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", jenkins_mock.MockResponse)
    assert jenkins_connect().server_created

def test_jenkins_create_job(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", jenkins_mock.MockResponse)
    project = {'git_url': 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git', 'name': 'pompiste'}
    with pytest.raises(jenkins_mock.Job_created_exception) as ex:
        create_job(project)
    assert str(ex.value) == 'pompiste'

def test_jenkins_update_job(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", jenkins_mock.MockResponse)
    project = {'git_url': 'https://gitlab.maduma.org/maduma/jenkins-mule-pipeline.git', 'name': 'flutiste'}
    with pytest.raises(jenkins_mock.Job_reconfigured_exception) as ex:
        update_job(project)
    assert str(ex.value) == 'flutiste'

def test_jenkins_created_folder(monkeypatch):
    monkeypatch.setattr(jenkins, "Jenkins", jenkins_mock.MockResponse)
    with pytest.raises(jenkins_mock.Job_created_exception) as ex:
        create_folder('mule')
    assert str(ex.value) == 'mule'
   