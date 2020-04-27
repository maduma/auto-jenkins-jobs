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
        pass

    def get_whoami(self):
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