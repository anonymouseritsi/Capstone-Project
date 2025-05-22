from django import forms
from .models import Patient, Procedure
from .models import Image
from .psgc import PSGCApi

class PatientForm(forms.ModelForm):
    region_code = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    province_code = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    city_municipality_code = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    barangay_code = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Patient
        fields = [
            'first_name', 'middle_name', 'last_name', 
            'age', 'sex', 'region_code', 'province_code',
            'city_municipality_code', 'barangay_code',
            'street', 'email', 'contact_number'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize region choices
        regions = PSGCApi.get_regions()
        region_choices = [('', '---Select Region---')] + [(r['code'], r['name']) for r in regions]
        self.fields['region_code'].widget.choices = region_choices

        # Initialize other fields with empty choices
        self.fields['province_code'].widget.choices = [('', '---Select Province---')]
        self.fields['city_municipality_code'].widget.choices = [('', '---Select City/Municipality---')]
        self.fields['barangay_code'].widget.choices = [('', '---Select Barangay---')]

        # If we have an instance with data or initial data, populate the choices
        if self.instance and self.instance.pk:
            if self.instance.region_code:
                provinces = PSGCApi.get_provinces(self.instance.region_code)
                self.fields['province_code'].widget.choices += [(p['code'], p['name']) for p in provinces]

            if self.instance.province_code:
                cities = PSGCApi.get_cities(self.instance.province_code)
                municipalities = PSGCApi.get_municipalities(self.instance.province_code)
                locations = [(c['code'], c['name']) for c in cities]
                locations += [(m['code'], m['name']) for m in municipalities]
                self.fields['city_municipality_code'].widget.choices += locations

            if self.instance.city_municipality_code:
                barangays = PSGCApi.get_barangays(
                    city_code=self.instance.city_municipality_code,
                    municipality_code=self.instance.city_municipality_code
                )
                self.fields['barangay_code'].widget.choices += [(b['code'], b['name']) for b in barangays]
        
        # If we have data from a POST request, validate and populate choices
        elif self.data:
            try:
                if self.data.get('region_code'):
                    provinces = PSGCApi.get_provinces(self.data['region_code'])
                    self.fields['province_code'].widget.choices += [(p['code'], p['name']) for p in provinces]

                if self.data.get('province_code'):
                    cities = PSGCApi.get_cities(self.data['province_code'])
                    municipalities = PSGCApi.get_municipalities(self.data['province_code'])
                    locations = [(c['code'], c['name']) for c in cities]
                    locations += [(m['code'], m['name']) for m in municipalities]
                    self.fields['city_municipality_code'].widget.choices += locations

                if self.data.get('city_municipality_code'):
                    barangays = PSGCApi.get_barangays(
                        city_code=self.data['city_municipality_code'],
                        municipality_code=self.data['city_municipality_code']
                    )
                    self.fields['barangay_code'].widget.choices += [(b['code'], b['name']) for b in barangays]
            except Exception as e:
                print(f"Error populating choices: {str(e)}")

    def clean(self):
        cleaned_data = super().clean()
        
        # If any address field is provided, all are required
        address_fields = ['region_code', 'province_code', 'city_municipality_code', 'barangay_code']
        provided_fields = [f for f in address_fields if cleaned_data.get(f)]
        
        if provided_fields and len(provided_fields) < len(address_fields):
            missing_fields = set(address_fields) - set(provided_fields)
            raise forms.ValidationError(
                f"Please complete all address fields. Missing: {', '.join(missing_fields)}"
            )

        # Validate PSGC codes
        if cleaned_data.get('province_code'):
            provinces = PSGCApi.get_provinces(cleaned_data.get('region_code'))
            valid_codes = [p['code'] for p in provinces]
            if cleaned_data['province_code'] not in valid_codes:
                self.add_error('province_code', 'Invalid province code')

        if cleaned_data.get('city_municipality_code'):
            cities = PSGCApi.get_cities(cleaned_data.get('province_code'))
            municipalities = PSGCApi.get_municipalities(cleaned_data.get('province_code'))
            valid_codes = [c['code'] for c in cities] + [m['code'] for m in municipalities]
            if cleaned_data['city_municipality_code'] not in valid_codes:
                self.add_error('city_municipality_code', 'Invalid city/municipality code')

        if cleaned_data.get('barangay_code'):
            barangays = PSGCApi.get_barangays(
                city_code=cleaned_data.get('city_municipality_code'),
                municipality_code=cleaned_data.get('city_municipality_code')
            )
            valid_codes = [b['code'] for b in barangays]
            if cleaned_data['barangay_code'] not in valid_codes:
                self.add_error('barangay_code', 'Invalid barangay code')

        return cleaned_data

class ProcedureForm(forms.ModelForm):
    class Meta:
        model = Procedure
        fields = ['procedure_type', 'notes']

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']