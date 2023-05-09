from django.db import models

# Create your models here.

class Faculty(models.Model):
    FacultyId = models.AutoField(primary_key=True)
    FacultyName = models.CharField(max_length=500,unique=True)
    FacultyPass = models.CharField(max_length=500)
    FacultyEmail = models.EmailField(null=False, blank=False)
