
class ContentChecker:
    def __init__(self, website):
        self.website = website
        self.content_rules = self.get_content_rules()

    def get_content_rules(self):
        return 0
    def verify(self, response):
        """
        raise content error
        """
        pass
"""
Checks the content of the web pages
"""