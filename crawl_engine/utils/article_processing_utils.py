import re
import mimetypes

from crawl_engine.exceptions import BlacklistedURLException


def is_url_blacklisted(url):
    """
    Checks if given url matches blacklisted resources. Reacts at the first occurrence.
    :param url:
    :return: boolean
    """
    # import is here in case of circular import problems
    from crawl_engine.models import BlockedSite

    blacklist = BlockedSite.objects.values_list('site', flat=True)
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
