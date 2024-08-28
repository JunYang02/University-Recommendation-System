from django.contrib import admin
from .models import University, Major, UniversityMajor

# Admin class for Major
class MajorAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Admin class for University
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'university_type', 'location')
    filter_horizontal = ('majors',)

# Admin class for UniversityMajors (if needed)
class UniversityMajorsAdmin(admin.ModelAdmin):
    list_display = ('university', 'major')  # Add the fields you want to display

# Register your models here
admin.site.register(University, UniversityAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(UniversityMajor, UniversityMajorsAdmin)