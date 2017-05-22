class ParserError(Exception):
    pass


class SearchParser:
    """ Base class for search engine parsers """
    def __init__(self, search_query='', depth=1, options={}):
        self.search_query = search_query
        self.depth = depth
        self.options = options

    def _new_article(self, article_url, title, body):
        """ Probably replace this with Article models """
        return {'article_url': article_url.strip(), 'title': title.strip(), 'body': body.strip()}
