class Error(Exception):
    """Base Error class for module"""

    def __init__(self, message, *args):
        # Set some exception infomation
        self.msg = message


class BlacklistedURLException(Error):
    def __init__(self, resource, *args):
        self.resource = resource
        super(BlacklistedURLException, self).__init__(resource, *args)