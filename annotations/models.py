from django.db import models
from django.utils.timezone import now  
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Patient(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    # name = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50, default="")
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, default="")
    age = models.PositiveIntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    contact_number = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}-{self.id}")
            self.slug = base_slug
            self.save(update_fields=['slug'])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    #procedure cost
    def total_procedure_cost(self):
        return sum(procedure.get_price() for procedure in self.procedures.all())

# class Procedure(models.Model):
#     PROCEDURE_CHOICES = [
#         ('abdominal', 'Abdominal'),
#         ('pelvic', 'Pelvic'),
#         ('obstetric', 'Obstetric'),
#         ('thyroid', 'Thyroid'),
#         ('breast', 'Breast'),
#     ]

#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='procedures', null=True)
#     procedure_type = models.CharField(max_length=20, choices=PROCEDURE_CHOICES) 
#     notes = models.TextField(blank=True, null=True)
#     date = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.procedure_type} - {self.patient.name}"

#procedure cost
class Procedure(models.Model):
    PROCEDURE_CHOICES = [
        ('abdominal', 'Abdominal'),
        ('pelvic', 'Pelvic'),
        ('obstetric', 'Obstetric'),
        ('thyroid', 'Thyroid'),
        ('breast', 'Breast'),
    ]

    PRICE_MAPPING = {
        'abdominal': 3000,
        'pelvic': 2000,
        'obstetric': 5000,
        'thyroid': 5500,
        'breast': 6000,
    }

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='procedures', null=True)
    procedure_type = models.CharField(max_length=20, choices=PROCEDURE_CHOICES) 
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.procedure_type} - {self.patient.name}"

    def get_price(self):
        return self.PRICE_MAPPING.get(self.procedure_type, 0)


class Image(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='images', null=True)
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True)
    annotated_image = models.ImageField(upload_to='annotated_images/', null=True, blank=True)
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
