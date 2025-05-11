from django.db import models
from django.utils.timezone import now  
from django.utils import timezone
from django.db import models
from django.conf import settings

class Patient(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Procedure(models.Model):
    PROCEDURE_CHOICES = [
        ('abdominal', 'Abdominal'),
        ('pelvic', 'Pelvic'),
        ('obstetric', 'Obstetric'),
        ('thyroid', 'Thyroid'),
        ('breast', 'Breast'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='procedures', null=True)
    procedure_type = models.CharField(max_length=20, choices=PROCEDURE_CHOICES) 
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=models.DateField.today)

    def __str__(self):
        return f"{self.procedure_type} - {self.patient.name}"

# class Image(models.Model):
#     title = models.CharField(max_length=255, blank=True, null=True)
#     image = models.ImageField(upload_to='images/')
#     def __str__(self):
#         return self.title if self.title else "Image"
class Image(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='images', null=True)
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Image for {self.patient.name} at {self.uploaded_at}"
    
class Annotation(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="annotations", null=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()
    label = models.CharField(max_length=255)

    def __str__(self):
        return f"Annotation on {self.image.title}"
