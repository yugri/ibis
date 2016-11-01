import mimetypes


def is_url_image(url):
    """
    Receives the url and checks if it is an image type
    :param url:
    :return: boolean
    """
    mimetype, encoding = mimetypes.guess_type(url)
    return mimetype and mimetype.startswith('image')