from django.db import models
from django.contrib.auth.models import User

class users(models.Model):
    name = models.CharField(max_length= 60)
    email = models.EmailField()
    password = models.CharField(max_length=128)

class Major(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class University(models.Model):
    name = models.CharField(max_length=255)
    university_type = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    admission = models.TextField(blank=True, null=True)
    faculty = models.CharField(max_length=70)
    program = models.CharField(max_length=50, blank=True, null=True)
    PreU = models.CharField(max_length=50, blank=True, null=True)
    Undergraduate = models.CharField(max_length=50, blank=True, null=True)
    Postgraduate = models.CharField(max_length=50, blank=True, null=True)
    Accommodation = models.CharField(max_length=50, blank=True, null=True)
    Ranking = models.CharField(max_length=50, blank=True, null=True)
    Image = models.ImageField(upload_to='university_logos/', blank=True, null=True)
    official_page = models.URLField(max_length=200, blank=True, null=True)
    majors = models.ManyToManyField(Major, through='UniversityMajor', related_name='universities')
    Recommendation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class UniversityMajor(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.university.name} - {self.major.name}"

# Create your models here.
