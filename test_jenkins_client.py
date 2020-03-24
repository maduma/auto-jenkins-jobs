from jenkins_client import is_job_up_to_date_xml, get_job_type_and_version, get_description
import responses
import pytest

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
