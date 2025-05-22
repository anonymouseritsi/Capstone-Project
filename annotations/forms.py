from django import forms
from .models import Patient, Procedure
from .models import Image

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'middle_name', 'last_name', 'age', 'sex', 'province', 'city_municipality', 'baranggay', 'street', 'email', 'contact_number']

class ProcedureForm(forms.ModelForm):
    class Meta:
        model = Procedure
        fields = ['procedure_type', 'notes']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']