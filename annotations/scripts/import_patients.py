import csv
from django.utils.text import slugify
from annotations.models import Patient

def run():
    with open('annotations/data/MOCK_DATA.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            slug = slugify(f"{row['first_name']}-{row['last_name']}")
            Patient.objects.create(
                first_name=row['first_name'],
                middle_name=row['middle_name'],
                last_name=row['last_name'],
                age=int(row['age']),
                sex=row['sex'],
                contact_number=row['contact_number'],
                province=row['province'],
                city_municipality=row['city'],
                baranggay=row['barangay'],
                street=row['street'],
                email=row['email'],
                slug=slug
            ) 