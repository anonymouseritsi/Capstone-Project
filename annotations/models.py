from django.db import models
from django.utils.timezone import now  

class Image(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    def __str__(self):
        return self.title if self.title else "Image"
class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="annotations")
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    label = models.CharField(max_length=255)

    def __str__(self):
        return f"Annotation on {self.image.title}"
