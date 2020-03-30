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

    def create_job(self, name, xml):
        raise Job_created_exception(name)

    def reconfig_job(self, name, xml):
        raise Job_reconfigured_exception(name)

    def build_job(self, name, parameters=None):
        raise Job_build_exception(name)