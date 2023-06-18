from django.db import models
from django.contrib.postgres.fields import HStoreField
from login.models import Faculty

class Year(models.Model):
    name = models.CharField(max_length=50)

class ExamId(models.Model):
    exam_id = models.CharField(max_length=10, unique=True)
    examname = models.CharField(max_length=500)

class Batch(models.Model):
    examid = models.ForeignKey(ExamId, on_delete=models.CASCADE,null=True)
    year = models.CharField(max_length=500)
    branch_name = models.CharField(max_length=500)
    exam_name=  models.CharField(max_length=500,null=True)
    exam_time = models.CharField(max_length=500, null=True)
    csv_file_path=models.FileField(upload_to='uploaded',null=True)


class Section(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50,null=True,blank=True)
    examid = models.ForeignKey(ExamId, on_delete=models.CASCADE,null=True)
    faculty = models.CharField(max_length=500,null=True,blank=True)
    seats = models.TextField(null=True, blank=True)
    file_path = models.CharField(max_length=500, null=True, blank=True)

    def get_roll_numbers(self):
        roll_numbers = []

        for row in self.seats:
            if row:
                roll_numbers.extend(row)

        return roll_numbers

    def _str_(self):
        return f"Section {self.class_id}"
    


class Student(models.Model):
    roll_no = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    batch = models.CharField(max_length=50)
    section = models.ForeignKey(Section, on_delete=models.CASCADE,null=True)
    examid = models.ForeignKey(ExamId, on_delete=models.CASCADE,null=True)
    seat_row = models.IntegerField()
    seat_column = models.IntegerField()
    attendance = models.BooleanField(default=False)  

    def _str_(self):
        return self.name


