class Job_created_exception(Exception):
    pass

class Job_reconfigured_exception(Exception):
    pass

class Job_build_exception(Exception):
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

    def get_job_name(self, name):
        if name != 'NO_JOB':
            return name
        else:
            return False

    def get_job_config(self, name):
        return 'XML'