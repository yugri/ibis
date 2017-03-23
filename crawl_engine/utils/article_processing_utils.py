import re
import mimetypes

from crawl_engine.utils.ibis_client import IbisClient
from crawl_engine.exceptions import BlacklistedURLException


def is_url_blacklisted(url):
    """
    Checks if given url matches blacklisted resources. Reacts at the first occurrence.
    :param url:
    :return: boolean
    """
    cli = IbisClient()
    try:
        r = cli.get('api/v1/blocked-sites')
    except ConnectionError:
        r = []
    blacklist = [x['site'] for x in r.json()]

    for resource in blacklist:
        if re.search(resource, url) is not None:
            exc = BlacklistedURLException(resource)
            raise exc


def is_url_image(url):
    """
    Receives the url and checks if it is an image type
    :param url:
    :return: boolean
    """
    mimetype, encoding = mimetypes.guess_type(url)
    return mimetype and mimetype.startswith('image')
