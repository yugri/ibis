class ParserError(Exception):
    pass


class SearchParser:
    """ Base class for search engine parsers """
    def __init__(self, search_query='', depth=1, options={}):
        self.search_query = search_query
        self.depth = depth
        self.options = options

    def _new_article(self, url, title, text):
        """ Probably replace this with Article models """
        return {'url': url.strip(), 'title': title.strip(), 'text': text.strip()}