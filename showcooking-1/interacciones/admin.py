from django.contrib import admin
from .models import YourModelName  # Replace with your actual model names

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2', 'field3')  # Replace with your actual fields
    search_fields = ('field1', 'field2')  # Replace with your actual fields
    list_filter = ('field3',)  # Replace with your actual fields

admin.site.register(YourModelName, YourModelAdmin)  # Register your model admin here