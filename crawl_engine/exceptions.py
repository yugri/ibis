class Error(Exception):
    """Base Error class for module"""

    def __init__(self, message, *args):
        # Set some exception infomation
        self.msg = message
