from django.db import models
from django.utils.timezone import now  
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from .psgc import PSGCApi

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
    
    # PSGC Fields
    region_code = models.CharField(max_length=9, blank=True)
    province_code = models.CharField(max_length=9, blank=True)
    city_municipality_code = models.CharField(max_length=9, blank=True)
    barangay_code = models.CharField(max_length=9, blank=True)
    
    # Human-readable address fields (automatically populated)
    province = models.CharField(max_length=100, default="")
    city_municipality = models.CharField(max_length=100, default="")
    baranggay = models.CharField(max_length=100, default="") 
    street = models.CharField(max_length=100, default="")
    
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)
    email = models.EmailField(blank=True)
    procedure = models.CharField(max_length=50, blank=True)

    def clean(self):
        cleaned_data = super().clean()
        errors = {}

        # Only validate if all address fields are provided
        if any([self.region_code, self.province_code, self.city_municipality_code, self.barangay_code]):
            # Validate province code
            if self.province_code:
                try:
                    provinces = PSGCApi.get_provinces(self.region_code)
                    if not any(p['code'] == self.province_code for p in provinces):
                        errors['province_code'] = 'Invalid province code'
                    else:
                        # Auto-populate province name
                        province_data = next((p for p in provinces if p['code'] == self.province_code), None)
                        if province_data:
                            self.province = province_data['name']
                except Exception as e:
                    print(f"Error validating province: {str(e)}")
                    errors['province_code'] = 'Error validating province code'

            # Validate city/municipality code
            if self.city_municipality_code:
                try:
                    cities = PSGCApi.get_cities(self.province_code) if self.province_code else []
                    municipalities = PSGCApi.get_municipalities(self.province_code) if self.province_code else []
                    all_locations = cities + municipalities
                    
                    if not any(l['code'] == self.city_municipality_code for l in all_locations):
                        errors['city_municipality_code'] = 'Invalid city/municipality code'
                    else:
                        # Auto-populate city/municipality name
                        location_data = next((l for l in all_locations if l['code'] == self.city_municipality_code), None)
                        if location_data:
                            self.city_municipality = location_data['name']
                except Exception as e:
                    print(f"Error validating city/municipality: {str(e)}")
                    errors['city_municipality_code'] = 'Error validating city/municipality code'

            # Validate barangay code
            if self.barangay_code:
                try:
                    barangays = PSGCApi.get_barangays(
                        city_code=self.city_municipality_code, 
                        municipality_code=self.city_municipality_code
                    )
                    if not any(b['code'] == self.barangay_code for b in barangays):
                        errors['barangay_code'] = 'Invalid barangay code'
                    else:
                        # Auto-populate barangay name
                        barangay_data = next((b for b in barangays if b['code'] == self.barangay_code), None)
                        if barangay_data:
                            self.baranggay = barangay_data['name']
                except Exception as e:
                    print(f"Error validating barangay: {str(e)}")
                    errors['barangay_code'] = 'Error validating barangay code'

            # Check if all required address fields are provided when any are
            address_fields = ['region_code', 'province_code', 'city_municipality_code', 'barangay_code']
            provided_fields = [f for f in address_fields if getattr(self, f)]
            if provided_fields and len(provided_fields) < len(address_fields):
                missing_fields = set(address_fields) - set(provided_fields)
                errors['__all__'] = f'Please complete all address fields. Missing: {", ".join(missing_fields)}'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}-{self.id}")
            self.slug = base_slug
            self.save(update_fields=['slug'])

    def get_absolute_url(self):
        return reverse('patient_manager:add_procedure', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    #procedure cost
    def total_procedure_cost(self):
        return sum(procedure.get_price() for procedure in self.procedures.all())


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
