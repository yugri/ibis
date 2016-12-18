from autoslug import AutoSlugField
from django.db import models


class Tag(models.Model):
    """
    Class for tagging/classification instances
    """
    name = models.CharField(max_length=200, db_index=True)
    slug = AutoSlugField(populate_from='name', always_update=True, unique=True)

    def __str__(self):
        return self.name
