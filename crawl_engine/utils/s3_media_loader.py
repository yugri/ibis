import io

from PIL import Image
from django.conf import settings
import requests
import logging
import boto


class ImageLoader:

    logger = logging.getLogger(__name__)

    def __init__(self, img_url):
        self.img_url = img_url

    def load(self):
        try:
            r = requests.get(self.img_url, stream=True)
        except requests.ConnectionError as e:
            r = None
            self.logger.error(e)

        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            self.logger.info("An image was loaded from buffer")

            return img
        return None