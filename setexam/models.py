from django.db import models
from django.contrib.postgres.fields import HStoreField
from login.models import Faculty


class Exam(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.CharField(max_length=20)

class Year(models.Model):
    name = models.CharField(max_length=50)

class Batch(models.Model):
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)

class UploadedCSV(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    file = models.FileField(upload_to='csv_files/')

class Allotment(models.Model):
    students = HStoreField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE,to_field='FacultyName')
    class_alloted = models.CharField(max_length=100)

class ExamId(models.Model):
    exam_id = models.CharField(max_length=10, unique=True)
    examname = models.CharField(max_length=100)
    examdate = models.DateField()
    examtime = models.CharField(max_length=20)

class ClassAllotted(models.Model):
    exam_id = models.ForeignKey(ExamId, on_delete=models.CASCADE, related_name='class_allotted')
    faculty_assigned = models.ForeignKey(Faculty,max_length=100, blank=True, null=True,on_delete=models.SET_NULL)
    classallotted = models.CharField(max_length=100, blank=True, null=True)
    csv_file = models.FileField(upload_to='csv_file/')