from django.db import models


class File(models.Model):
    title = models.TextField(max_length=255)
    blurInt = models.IntegerField()
    keysession = models.TextField(max_length=200)
    outputPath = models.TextField(max_length=255)
    img = models.ImageField(upload_to='photos/', max_length=254)

    @property
    def photo_url(self):
        if self.outputPath and hasattr(self.outputPath, 'url'):
            return self.outputPath.url
