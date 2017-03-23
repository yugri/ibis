import re
import mimetypes

from crawl_engine.exceptions import BlacklistedURLException
from crawl_engine.utils.ibis_client import IbisClient


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

    if r.status_code == '200':
        blacklist = [x['site'] for x in r.json()]
    else:
        blacklist = []

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
