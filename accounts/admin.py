from django.contrib import admin
from .models import CustomUser, Invoice, Statement

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Invoice)
admin.site.register(Statement)