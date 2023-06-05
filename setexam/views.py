# Create your views here.
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Exam, Year, Batch, UploadedCSV
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Exam, Year, Batch, UploadedCSV
import json
from django.core.files.base import ContentFile
import os
import csv
import json
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Allotment
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.forms import HStoreField as HStoreFormField
from login.models import Faculty
import numpy as np
import random
from django.shortcuts import get_object_or_404
from .models import ClassAllotted
from .models import ExamId

@csrf_exempt

def get_exam_names(request):
    exams = ExamId.objects.all().values('exam_id', 'examname')
    return JsonResponse(list(exams), safe=False)

@csrf_exempt

def get_exam_details(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            exam_name = payload.get('examName')
            exam_date = payload.get('examDate')
            exam_time = payload.get('examTime')

            print(f'Name: {exam_name}, Date: {exam_date}, Time: {exam_time}')

            if not (exam_name and exam_date and exam_time):
                return JsonResponse({'error': 'Exam name, date, and time are required.'}, status=400)

            """ exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()  """ # Convert date string to date object

            # Generate a random 4-digit number for examid
            examid = random.randint(1000, 9999)

            exam = ExamId.objects.create(exam_id=str(examid), examname=exam_name, examdate=exam_date, examtime=exam_time)

            return JsonResponse({'exam_id': exam.exam_id})
        except Exception as e:
            print(f'Error: {e}')
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        try:
            exam_id = request.POST.get('exam_id')
            year_name = request.POST.get('year_name')
            exam_time = request.POST.get('exam_time')
            branch = request.POST.get('branch_time')
            csv_file = request.FILES.get('csv_file')

            # Create a unique file name
            file_name = f"{exam_id}/{year_name}/{branch}.csv"

            # Save the CSV file locally
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded', file_name)
            fs = FileSystemStorage()
            fs.save(file_path, csv_file)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

@csrf_exempt

def get_exam_details_front(request, examname):
    try:
        exam = ExamId.objects.get(examname=examname)
        class_allotted = exam.class_allotted.first()
        exam_details = {
            'exam_id': exam.exam_id,
            'examname': exam.examname,
            'examdate': exam.examdate.strftime('%Y-%m-%d'),
            'examtime': exam.examtime,
            'faculty_assigned': class_allotted.faculty_assigned.FacultyName if class_allotted else None,
            'classallotted': class_allotted.classallotted if class_allotted else None,
            'csv_file': class_allotted.csv_file.url if class_allotted else None,
        }
        return JsonResponse(exam_details, safe=False)
    except ExamId.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)

@csrf_exempt

def classallotment(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            exam_id = payload.get('examId')
            print(f'The exam_id is :{exam_id}')

            exam = get_object_or_404(ExamId, exam_id=exam_id)

            uploaded_folder = os.path.join('uploaded', exam_id)
            year_folders = ['year 1', 'year 2', 'year 3', 'year 4']
            branch_files = {}

            for year_folder in year_folders:
                year_path = os.path.join(uploaded_folder, year_folder)

                if os.path.isdir(year_path):
                    branch_files[year_folder] = {}

                    for branch_file in os.listdir(year_path):
                        if branch_file.endswith('.csv'):
                            branch_name = os.path.splitext(branch_file)[0]
                            branch_files[year_folder][branch_name] = os.path.join(year_path, branch_file)

            # Allotment logic
            class_count = 1
            allotted_data = []

            for year, branches in branch_files.items():
                for branch_name, branch_file_path in branches.items():
                    data = []

                    with open(branch_file_path, 'r') as csv_file:
                        csv_reader = csv.reader(csv_file)

                        next(csv_reader)

                        for row in csv_reader:
                            roll_no = row[1]
                            name = row[2]
                            data.append((roll_no, name))

                    allotted_data.extend(data)

            random.shuffle(allotted_data)

            allotted_folder = os.path.join('allotted', exam_id)
            os.makedirs(allotted_folder, exist_ok=True)
            remaining_students = len(allotted_data)

            while remaining_students > 0:
                allotted_file_path = os.path.join(allotted_folder, f'class{class_count}.csv')
                num_students = min(45, remaining_students)
                class_students = allotted_data[:num_students]
                allotted_data = allotted_data[num_students:]
                remaining_students -= num_students

                with open(allotted_file_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for row in class_students:
                        csv_writer.writerow(row)

                ClassAllotted.objects.create(exam_id=exam_id, csv_file=f'class{class_count}.csv')
                ClassAllotted.save()
                class_count += 1

            return JsonResponse({'message': 'Allotment process completed successfully.'})

        except Exception as e:
            return JsonResponse({'error': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method.'})