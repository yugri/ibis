from django.core.files.storage import get_storage_class
from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin, ManifestFilesMixin
from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
# from filebrowser_safe.storage import S3BotoStorageMixin


class CachedS3BotoStorage(PipelineMixin, CachedFilesMixin, S3BotoStorage):

    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        name = super(CachedS3BotoStorage, self).save(name, content)
        self.local_storage._save(name, content)
        return name


class S3BotoStorage(PipelineMixin, ManifestFilesMixin, S3BotoStorage):
    """
    Use this unless you don't have access to the local file system
    """
    pass


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION


StaticStorage = lambda: CachedS3BotoStorage(location=settings.STATICFILES_LOCATION)
