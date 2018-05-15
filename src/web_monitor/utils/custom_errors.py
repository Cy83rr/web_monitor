class ContentError(Exception):
    """
    Raise when the website request was fine, but the content wasn't as specified
    """


class ConnectionProblem(Exception):
    """
    Raise when there are connection level problem, eg. the website is down
    """
