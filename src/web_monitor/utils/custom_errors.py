class ContentError(Exception):
    """
    Raise when the website request was fine, but the content wasn't as specified
    """


class ConnectionProblem(Exception):
    """
    Raise when there are connection level problem, eg. the website is down
    """
    def __init__(self, url, error_msg):
        super(ConnectionProblem, self).__init__()
        self.url = url
        self.error_msg = error_msg