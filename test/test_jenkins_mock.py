class Job_created_exception(Exception):
    pass

class Job_reconfigured_exception(Exception):
    pass

class Job_build_exception(Exception):
    pass

class Run_script_exception(Exception):
    pass

class MockResponse:

    server_created = False

    database = [
        {'type'}

    ]

    def __init__(self, server, username, password, timeout):
        self.server_created = True
        print(server)
        if server == 'BAD':
            raise Exception('SERVER_ERROR')
        if password == 'BAD':
            raise Exception('AUTHENTICATION_ERROR')
        pass

    def get_whoami(self):
        self.whoami = 'jenkins'
        pass 

    def get_version(self):
        self.whoami = 'jenkins'
        pass 

    def create_job(self, name, xml):
        raise Job_created_exception(name)

    def reconfig_job(self, name, xml):
        raise Job_reconfigured_exception(name)

    def build_job(self, name, parameters=None):
        raise Job_build_exception(name)

    def run_script(self, script):
        raise Run_script_exception()

    def get_job_name(self, name):
        if name != 'NO_JOB':
            return name
        return False

    def get_job_config(self, name):
        if name == 'job1':
            return "<top><description></description></top>"
        elif name == 'job2':
            return "<top><description>Auto Jenkins Job, mulePipeline:0.0.1</description></top>"
        elif name == 'job3':
            return "<top><description>Auto Jenkins Job, mulePipeline:0.0.2</description></top>"
        return 'XML'