from django.db import models
from django.contrib.postgres.fields import HStoreField
from login.models import Faculty


# class Exam(models.Model):
#     name = models.CharField(max_length=100)
#     # date = models.DateField()
#     # time = models.CharField(max_length=20)

class Year(models.Model):
    name = models.CharField(max_length=50)

class ExamId(models.Model):
    exam_id = models.CharField(max_length=10, unique=True)
    examname = models.CharField(max_length=500)
    # examdate = models.DateField(null=True)
    # examtime = models.CharField(null=True, max_length=20)

class Batch(models.Model):
    examid = models.ForeignKey(ExamId, on_delete=models.CASCADE,null=True)
    year = models.CharField(max_length=500)
    branch_name = models.CharField(max_length=500)
    exam_name=  models.CharField(max_length=500,null=True)
    exam_time = models.CharField(max_length=500, null=True)
    csv_file_path=models.FileField(upload_to='uploaded',null=True)

    # def __str__(self):
    #     return f"{self.exam_id.exam_id} - {self.year_name} - {self.branch_name}"
    
    

# class UploadedCSV(models.Model):
#     exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
#     year = models.ForeignKey(Year, on_delete=models.CASCADE)
#     batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
#     file = models.FileField(upload_to='csv_files/')

# class Allotment(models.Model):
#     students = HStoreField()
#     faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE,to_field='FacultyName')
#     class_alloted = models.CharField(max_length=100)



# class ClassAllotted(models.Model):
#     # exam_id = models.ForeignKey(ExamId, on_delete=models.CASCADE, related_name='class_allotted')
#     class_id = class_id = models.AutoField(primary_key=True)
#     faculty_assigned = models.ForeignKey(Faculty,max_length=100, blank=True, null=True,on_delete=models.SET_NULL)  
#     classallotted = models.CharField(max_length=100, blank=True, null=True)
#     csv_file = models.FileField(upload_to='csv_file/')



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

    def __str__(self):
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

    def __str__(self):
        return self.name



