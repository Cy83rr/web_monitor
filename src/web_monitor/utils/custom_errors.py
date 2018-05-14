class ContentError(Exception):
    """
    Raise when the website request was fine, but the content wasn't as specified
    """