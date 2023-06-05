from django.db import models

# Create your models here.
class malpractice(models.Model):
    StudentId = models.AutoField(primary_key=True)
    StudentName = models.CharField(max_length=500)
    StudentRegister = models.CharField(max_length=500,unique=True)
    StudentClass = models.CharField(max_length=500)
    StudentBatch = models.CharField(max_length=500)
    StudentInvigilator = models.CharField(max_length=500)
    StudentRemark = models.CharField(max_length=500)
