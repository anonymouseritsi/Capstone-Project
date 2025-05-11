from django import forms
from .models import Patient, Procedure
from .models import Image

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'sex', 'contact_number']

class ProcedureForm(forms.ModelForm):
    class Meta:
        model = Procedure
        fields = ['patient', 'procedure_type', 'notes', 'date']
    date = forms.DateField(widget=forms.SelectDateWidget())

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']