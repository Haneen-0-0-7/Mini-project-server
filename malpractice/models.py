from django.db import models

# Create your models here.
class malpractice(models.Model):
    StudentId = models.AutoField(primary_key=True)
    StudentRegister = models.CharField(max_length=500,unique=True)
    StudentInvigilator = models.CharField(max_length=500)
    StudentRemark = models.CharField(max_length=500)
