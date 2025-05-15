from django.contrib import admin
from .models import *


admin.site.register(Procedure)
admin.site.register(Patient)
admin.site.register(Image)
admin.site.register(Annotation)
