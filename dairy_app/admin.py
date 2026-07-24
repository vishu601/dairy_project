from django.contrib import admin
from .models import Farmer, MilkCollection

# Yeh dono lines zaroori hain taaki admin panel par tables dikhein
admin.site.register(Farmer)
admin.site.register(MilkCollection)