# Create your views here.
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import  Batch
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import  Batch, Section
import json
from django.core.files.base import ContentFile
import os
import csv
import json
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.postgres.fields import HStoreField
from django.contrib.postgres.forms import HStoreField as HStoreFormField
from login.models import Faculty
import numpy as np
import random
from django.shortcuts import get_object_or_404
from login.models import Faculty
# from .models import ClassAllotted
from .models import ExamId
import math
import pandas as pd


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
            # exam_date = payload.get('examDate')
            # exam_time = payload.get('examTime')

            print(f'Name: {exam_name}')

            if not (exam_name):
                return JsonResponse({'error': 'Exam name, date, and time are required.'}, status=400)

            """ exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()  """ # Convert date string to date object

            # Generate a random 4-digit number for examid
            examid = random.randint(1000, 9999)

            exam = ExamId.objects.create(exam_id=str(examid), examname=exam_name)

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
            id = request.POST.get('exam_id')
            year_name = request.POST.get('year_name')
            # exam_time = request.POST.get('exam_time')
            branch = request.POST.get('branch_time')
            csv_file = request.FILES.get('csv_file')
            print(branch)
            
            # Create a unique file name
            file_name = f"{id}/{year_name}/{branch}.csv"

            # Save the CSV file locally
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded', file_name)
            fs = FileSystemStorage()
            fs.save(file_path, csv_file)
            print(file_path)
            print('hello')
            batch = Batch.objects.create(
                examid = ExamId.objects.get(exam_id=id),
                year = year_name,
                branch_name=branch,
                csv_file_path = file_path
            )

            return JsonResponse({'status': 'success', 'batch_id': batch.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def get_exam_details_front(request, id):
    try:
        exam = ExamId.objects.get(exam_id=id)
        print(exam)
        print(id)
        sections = Section.objects.filter(examid=exam)
        print(sections)
        # Retrieve all faculty usernames from the Faculty table
        faculty_usernames = Faculty.objects.values_list('FacultyName', flat=True)
        print(faculty_usernames)
        # Shuffle the list of faculty usernames
     

        k=0
        alloted_faculty = []
        for section in sections:
            section.faculty = faculty_usernames[k]
            k += 1
            section.save()
            alloted_faculty.append({'classid': section.class_id, 'faculty':section.faculty})
        exam_details = {
            'exam_id': exam.exam_id,
            'examname': exam.examname,
            'alloted_faculty': alloted_faculty
            # 'examdate': exam.examdate.strftime('%Y-%m-%d'),
            # 'examtime': exam.examtime,
            # 'faculty_assigned': class_allotted.faculty_assigned.FacultyName if class_allotted else None,
            # 'classallotted': class_allotted.classallotted if class_allotted else None,
            # 'csv_file': class_allotted.csv_file.url if class_allotted else None,


            #Create a dataframe with the alloted faculty data

        }
        return JsonResponse(exam_details, safe=False)
    except ExamId.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)

# def get_exam_details_front(request, id):
#     try:
#         exam = ExamId.objects.get(exam_id=id)
#         class_allotted = exam.class_allotted.first()
#         exam_details = {
#             'exam_id': exam.exam_id,
#             'examname': exam.examname,
#             # 'examdate': exam.examdate.strftime('%Y-%m-%d'),
#             # 'examtime': exam.examtime,
#             # 'faculty_assigned': class_allotted.faculty_assigned.FacultyName if class_allotted else None,
#             # 'classallotted': class_allotted.classallotted if class_allotted else None,
#             # 'csv_file': class_allotted.csv_file.url if class_allotted else None,
#         }
#         return JsonResponse(exam_details, safe=False)
#     except ExamId.DoesNotExist:
#         return JsonResponse({'error': 'Exam not found'}, status=404)

# @csrf_exempt
# def classallotment(request):
#     if request.method == 'POST':
#         try:
#             payload = json.loads(request.body)
#             exam_id = payload.get('examId')
#             print(f'The exam_id is: {exam_id}')

#             exam = get_object_or_404(ExamId, exam_id=exam_id)

#             uploaded_folder = os.path.join('uploaded/uploaded', exam_id)
#             year_folders = ['year 1', 'year 2', 'year 3', 'year 4']
#             branch_files = {}

#             for year_folder in year_folders:
#                 year_path = os.path.join(uploaded_folder, year_folder)

#                 if os.path.isdir(year_path):
#                     branch_files[year_folder] = {}

#                     for branch_file in os.listdir(year_path):
#                         if branch_file.endswith('.csv'):
#                             branch_name = os.path.splitext(branch_file)[0]
#                             branch_files[year_folder][branch_name] = os.path.join(year_path, branch_file)

#             # Allotment logic
#             class_count = 1
#             remaining_students = []
            

#             for year, branches in branch_files.items():
#                 for branch_name, branch_file_path in branches.items():
#                     data = []

#                     with open(branch_file_path, 'r') as csv_file:
#                         csv_reader = csv.reader(csv_file)

#                         next(csv_reader)

#                         for row in csv_reader:
#                             roll_no = row[1]
#                             name = row[2]
#                             data.append((roll_no, name))

#                     remaining_students.extend(data)
#             # print(remaining_students)
#             allotted_folder = os.path.join('allotted', exam_id)
#             os.makedirs(allotted_folder, exist_ok=True)
#             no_of_class =math.ceil(len(remaining_students)/45)
#             print(no_of_class)
#             last = []
#             while len(remaining_students) > 0:
                
#                 allotted_file_path = os.path.join(allotted_folder, f'class{class_count}.csv')
                
#                 while no_of_class > 0:
#                     chk1 = 0
#                     chk2 = 0
#                     section_data = [[None] * 9 for _ in range(5)]  # Initialize an empty 5x9 array
#                     student1 = remaining_students[0]
#                     batch1_students = [student for student in remaining_students if student[0][:5] == student1[0][:5]]
#                     if len(batch1_students)<25:
#                         last.extend(batch1_students)
#                     else:
#                         first_25_students = batch1_students[:25]
#                         print(first_25_students)
#                         print('\n')
                    
#                     diff_batch_students = [student for student in remaining_students if student[0][:5] != student1[0][:5]]
#                     print(diff_batch_students)
#                     student2 = diff_batch_students[0]
#                     batch2_students = [student for student in remaining_students if student[0][:5] == student2[0][:5]]
                    
#                     if len(batch1_students)<20:
#                         last.extend(batch2_students)
#                     else:
#                         second_20_students = batch2_students[:20]
#                         print(second_20_students,end='\t')
#                         print('\n')


#                     if(len(first_25_students) == 25):
#                         row=0
#                         col=0
#                         while col<9:
#                             row = 0
#                             while row < 5:
#                                 section_data[row][col] = first_25_students[0]
#                                 x = first_25_students[0]
#                                 # print(x)
#                                 remaining_students.remove(x)
#                                 del first_25_students[0]
                                
#                                 row += 1
#                             col += 2
#                             chk1= 1
#                     if(len(second_20_students) == 20)  :
#                         row2=0
#                         col2=1
#                         while col<8:
#                             row = 0
#                             while row < 5:
#                                 section_data[row2][col2] =second_20_students[0]
#                                 x = second_20_students[0]
#                                 # print(x)
#                                 remaining_students.remove(x)
#                                 del second_20_students[0]

#                                 row += 1
#                             col += 2
#                             chk2 = 1
#                     if chk1==1 and chk2 == 1:
#                         class_count += 1
#                         section = Section(class_id=class_count, seats=json.dumps(section_data),examid=exam)
#                         section.save()
#                     no_of_class -= 1

                
                
                
                
                

#             return JsonResponse({'message': 'Allotment process completed successfully.'})

#         except Exception as e:
#             return JsonResponse({'error': str(e)})

#     else:
#         return JsonResponse({'error': 'Invalid request method.'})



from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
import os
import csv
import numpy as np
import random


@csrf_exempt
def classallotment(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            exam_id = payload.get('examId')
            print(f'The exam_id is: {exam_id}')

            exam = get_object_or_404(ExamId, exam_id=exam_id)

            uploaded_folder = os.path.join('uploaded/uploaded', exam_id)
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
            leftover_students = []

            for year, branches in branch_files.items():
                for branch_name, branch_file_path in branches.items():
                    data = []

                    with open(branch_file_path, 'r') as csv_file:
                        csv_reader = csv.reader(csv_file)

                        next(csv_reader)

                        for row in csv_reader:
                            roll_no = row[1]
                            name = row[2]
                            batch = roll_no[:5]
                            data.append((roll_no, name, batch))

                    allotted_data.extend(data)

            # random.shuffle(allotted_data)

            allotted_folder = os.path.join('allotted', exam_id)
            os.makedirs(allotted_folder, exist_ok=True)
            remaining_students = len(allotted_data)
            total_seats = 45  # Total seats available in each class

            while remaining_students > 0:
                class_students = []
                num_students = min(total_seats, remaining_students)

                for _ in range(num_students):
                    if allotted_data:
                        student = allotted_data.pop(0)
                        class_students.append(student)
                    else:
                        break

                remaining_students -= num_students

                if len(class_students) < total_seats:
                    leftover_students.extend(class_students)
                    continue

                class_seats = np.empty((5, 9), dtype=object)
                class_seats.fill(None)

                # Allocate students to seats
                for i, student in enumerate(class_students):
                    seat_row = i // 9  # Rows 0, 1, 2, 3, 4
                    seat_column = i % 9  # Columns 0, 1, 2, 3, ..., 8
                    roll_no, name, batch = student
                    section = batch[4]
                    class_seats[seat_row, seat_column] = {'roll_no': roll_no, 'name': name, 'section': section}

                # Create and save the Section object
                section = Section.objects.create(class_id=class_count,examid= exam, seats=json.dumps(class_seats.tolist()))

                class_count += 1

            # Allot the leftover students
            if leftover_students:
                num_leftover_students = len(leftover_students)
                num_remaining_seats = total_seats - num_leftover_students
                class_seats = np.empty((5, 9), dtype=object)
                class_seats.fill(None)

                # Allocate leftover students to seats
                for i, student in enumerate(leftover_students):
                    seat_row = i // num_remaining_seats  # Rows 0, 1, 2, 3, 4
                    seat_column = i % num_remaining_seats  # Columns 0, 1, 2, 3, ..., num_remaining_seats-1
                    roll_no, name, batch = student
                    section = batch[4]
                    class_seats[seat_row, seat_column] = {'roll_no': roll_no, 'name': name, 'section': section}

                # Create and save the Section object for leftover students
                section = Section.objects.create(class_id=class_count, examid= exam, seats=json.dumps(class_seats.tolist()),)

            return JsonResponse({'message': 'Allotment process completed successfully.'})

        except Exception as e:
            return JsonResponse({'error': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method.'})



import csv
from django.http import HttpResponse
from .models import Section

def download_seats_csv(request, class_id):
    try:
        print(class_id)
        section = Section.objects.get(class_id=class_id)
        seats_data = eval(section.seats)  # Assuming the seats field contains a string representation of a list
        print(section)
        # Create a CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="seats_data.csv"'

        # Create a CSV writer
        writer = csv.writer(response)

        # Write the header row
        writer.writerow(['Roll No', 'Name', 'Section'])

        # Write the data rows
        for sublist in seats_data:
             if len(sublist) >= 9:
                writer.writerow(sublist[:9])  # Slice the sublist up to index 8
            
        print(response)    
        return response

    except Section.DoesNotExist:
        return HttpResponse(status=404)

