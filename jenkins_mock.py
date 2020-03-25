class Job_created_exception(Exception):
    pass

class Job_reconfigured_exception(Exception):
    pass

class MockResponse:

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