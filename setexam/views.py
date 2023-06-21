from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import  Batch
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import  Batch, Section, Student
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
from .models import ExamId
import math
import pandas as pd
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags



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

            if not (exam_name):
                return JsonResponse({'error': 'Exam name, date, and time are required.'}, status=400)

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
            
            df = pd.read_csv(csv_file)
            print(df)
            # Create a unique file name
            file_name = f"{id}/{year_name}/{branch}.csv"

            # Save the CSV file locally
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded', file_name)
            fs = FileSystemStorage()
            fs.save(file_path, csv_file)
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
    
@csrf_exempt
def get_exam_details_front(request, id):
    try:
        exam = ExamId.objects.get(exam_id=id)
        sections = Section.objects.filter(examid=exam)
        # Retrieve all faculty usernames from the Faculty table
        faculty_usernames = Faculty.objects.values_list('FacultyName', flat=True)
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

        }
        return JsonResponse(exam_details, safe=False)
    except ExamId.DoesNotExist:
        return JsonResponse({'error': 'Exam not found'}, status=404)

from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
import os
import csv
import numpy as np
import random
import re


@csrf_exempt
def display(request,examid):
        if request.method == 'GET':
            try:
             # sections = Section.objects.all().values('class_id')
             exam = ExamId.objects.get(exam_id=examid)
             sections = Section.objects.filter(examid=exam)
             data = []
             for section in sections:
                section_data = {
                    'class_id': section.class_id,
                    'class_name': section.class_name,
                    'faculty': section.faculty,
                }
                data.append(section_data)

             return JsonResponse(data, safe=False)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
@csrf_exempt
def classallotment(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            exam_id = payload.get('examId')
            examid_object = ExamId.objects.get(exam_id = exam_id)

            # Retrieve batches for the exam_id
            batch_objects = Batch.objects.filter(examid=examid_object)
            # print(batch_objects)

            # Process the files and create Student objects
            students_list, branch_students_list = process_files(batch_objects)
            

            # Initialize counters and lists
            batch_index = 0
            selected_students = []
            remaining_students = []
            next_batch_students = []
            count = 1
            x = "hello"
            i = 1
            while len(students_list) > 0:
                # Select 25 students from the current batch
                if len(branch_students_list[batch_index]) >= 25:
                    current_batch_students = branch_students_list[batch_index][:25]
                    selected_students.extend(current_batch_students[:25])
                    # Delete selected students from students_list
                    students_list = [student for student in students_list if student not in current_batch_students]
                    # Remove selected students from the current batch in branch_students_list
                    branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in current_batch_students]
                    
                else:
                    remaining_students.extend(branch_students_list[batch_index])
                    # Delete remaining students from students_list
                    students_list = [student for student in students_list if student not in remaining_students]
                    # Remove remaining students from the current batch in branch_students_list
                    branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in remaining_students]
                    current_batch_students = []
                    


                # Switch to the next batch index in a cyclic manner
                batch_index = (batch_index + 1) % len(branch_students_list)
        
                # Select 20 students from the next batch
                if len(branch_students_list[batch_index][:20]) >= 20:
                    next_batch_students = branch_students_list[batch_index][:20]
                    selected_students.extend(next_batch_students[:20])
        
                    # Delete selected students from students_list
                    students_list = [student for student in students_list if student not in next_batch_students]

                    # Remove selected students from the next batch in branch_students_list
                    branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in next_batch_students]

    
                else:           
                    remaining_students.extend(branch_students_list[batch_index][:20])
                   # Delete remaining students from students_list
                    students_list = [student for student in students_list if student not in remaining_students]

                    # Remove remaining students from the current batch in branch_students_list
                    branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in remaining_students]
                    next_batch_students
                    
    

                

                # Allotment
                if len(next_batch_students) > 0 and len(current_batch_students) > 0:
                    class_seats,count = allot(current_batch_students,next_batch_students,examid_object,count )
                    i += 1
                    
                

                # Switch to the next batch index in a cyclic manner
                batch_index = (batch_index + 1) % len(branch_students_list)
            first = []
            second = []
            #Alloting the remaining students
            while len(remaining_students) >= 45:
                first = remaining_students[:25]
                second = remaining_students[:20]
                class_seats,count = allot(first,second,examid_object,count)
                # Delete allotted students from remaining_students list
                remaining_students = remaining_students[45:]
                
            while len(remaining_students)>25:
                first = remaining_students[:25]
                class_seats,count = allot(first, [],examid_object,count)

                # Delete allotted students from remaining_students list
                remaining_students = remaining_students[25:]

            # Handle the remaining students (less than 25)
            if len(remaining_students) > 0:
                class_seats, count = allot(remaining_students, [],examid_object,count)
                remaining_students = []

            
            return JsonResponse({'message': 'Allotment completed successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def process_files(batch_objects):
    students = []
    branch_names = []
    branch_students = []

    for batch in batch_objects:
        branch_names.append(batch.branch_name)
        file_path = batch.csv_file_path.path

        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            # reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            branch_students.append([])  # Create an empty list for each branch

            # for row in reader:
            #     roll_no = row[0]
            #     name = row[1]
            #     batch_name = batch.year + ' ' + batch.branch_name
            for row in reader:
                roll_no = row['Roll_No']
                name = row['Name']
                batch_name = batch.year + ' ' + batch.branch_name

                std = Student.objects.create(
                    roll_no=roll_no,
                    name=name,
                    batch=batch_name,
                    examid=batch.examid,
                    seat_row=0,
                    seat_column=0,
                    attendance=False
                )
                student = {
                    'roll_no': roll_no,
                    'name': name,
                    'batch': batch_name,
                    'examid': batch.examid,
                    'seat_row': 0,
                    'seat_column': 0,
                    'attendance': False
                }
                students.append(student)
                branch_students[-1].append(student)  # Append student to the last branch list

    return students, branch_students

@csrf_exempt
def allot(first_batch_students, second_batch_students,examid_object,count):
    section = Section()
    allotted_folder = os.path.join('allotted', str(examid_object.id))
    os.makedirs(allotted_folder, exist_ok=True)
    class_seats = np.empty((5, 9), dtype=object)
    class_seats.fill(None)
    current_row = 0
    even_columns = [i for i in range(0, 9, 2)]
    odd_columns = [i for i in range(1, 9, 2)]
    
    section = Section.objects.create(examid=examid_object)  # Create the Section object

    for i, student in enumerate(first_batch_students):
        row = current_row
        col = even_columns[i % len(even_columns)]
        class_seats[row, col] = student
        student_object = Student.objects.get(roll_no = student['roll_no'],examid=student['examid'])
        student_object.section = section
        student_object.save()



         # Check if we have filled all the seats in the current row
        if (i + 1) % 5 == 0:
            current_row += 1  # Move to the next row

            # Reset the column index to 0
            if current_row < 5:
                col = even_columns[0]
            else:
                break  # Exit the loop if all rows are filled
            #
            

    
    current_row = 0
    for i, student in enumerate(second_batch_students):
        row = current_row
        col = odd_columns[i % len(odd_columns)]
        class_seats[row, col] = student
         # Assuming roll_no is the key to match with seat
        student_object = Student.objects.get(roll_no = student['roll_no'],examid=student['examid'])
        student_object.section = section
        student_object.save()

        

        if (i + 1) % 4 == 0:
            current_row += 1
            if current_row < 5:
                col = odd_columns[0]
            else:
                break

    # Create a unique file name for each function call using the count
    file_name = f'class_allotment_{count}.csv'
    file_path = os.path.join(allotted_folder, file_name)
            
    
    section.examid = examid_object
   
    # Write roll numbers to the unique CSV file
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in class_seats:
            row_roll_numbers = []
            for seat in row:
                if seat is not None:
                    roll_number = seat['roll_no']
                    row_roll_numbers.append(roll_number)
                else:
                     row_roll_numbers.append("None")
            csv_writer.writerow(row_roll_numbers)
    section.file_path = file_path
    section.save()


    count += 1

    # Loop to print the entire matrix with student roll numbers
    for row in class_seats:
        for seat in row:
            if seat is None:
                print("Empty", end="\t")
            else:
                roll_number = seat['roll_no']

    return class_seats, count


@csrf_exempt
def download_seats_csv(request, class_id):
    try:
        section = Section.objects.get(class_id=class_id)
        file_path = section.file_path

        # Open the CSV file in binary mode
        with open(file_path, 'rb') as csv_file:
            response = HttpResponse(csv_file.read(), content_type='text/csv')
            # Set the Content-Disposition header for file download
            response['Content-Disposition'] = 'attachment; filename="data.csv"'
            return response
    except Exception as e:
        return JsonResponse({'error': str(e)})




@csrf_exempt
def process_form_data(request):
    if request.method == 'POST':
        form_data = json.loads(request.body)
        data_list = form_data['data']
        for data in data_list:
            class_id = data['classId']
            faculty_name = data['facultyName']
            class_allotted = data['classAllotted']

            # Get the Section object based on class_id
            section = Section.objects.get(class_id=class_id)

            # Update the faculty and class name fields
            section.faculty = faculty_name
            section.class_name = class_allotted

            # Save the changes
            section.save()
            

            # Get the faculty email based on faculty name
            faculty = Faculty.objects.get(FacultyName=faculty_name)
            faculty_email = faculty.FacultyEmail
            file_path = section.file_path
            # Print the file+path
            print("File Path:", file_path)


            # Get the faculty email based on faculty name
            faculty = Faculty.objects.get(FacultyName=faculty_name)
            faculty_email = faculty.FacultyEmail

            exam_id = section.examid
            examname = exam_id.examname

            # Send email to the faculty
            subject = 'Attendance Notification'
            html_content = render_to_string('attendance_email.html', {'faculty_name': faculty_name, 'class_allotted': class_allotted,'examname': examname})
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(subject, text_content, to=[faculty_email])
            email.attach_alternative(html_content, 'text/html')

            # Attach the CSV file to the email
            csv_file_path = section.file_path
            csv_file_name = 'attendance.csv'  # Provide a desired name for the CSV file
            with open(csv_file_path, 'rb') as csv_file:
                email.attach(csv_file_name, csv_file.read(), 'text/csv')

            email.send()
        
        return JsonResponse({'message': 'Form data processed successfully.'})
    else:
        return JsonResponse({'message': 'Invalid request method.'})
    
@csrf_exempt
def get_classnames(request, exam_name):
    if request.method == 'GET':
        sections = Section.objects.filter(examid__examname=exam_name)
        class_names = [section.class_name for section in sections]
        return JsonResponse({'class_names': class_names})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def get_attendance(request, exam_name, class_name):
    if request.method == 'GET':
        section = Section.objects.filter(examid__examname=exam_name, class_name=class_name).first()
        if section:
            students = Student.objects.filter(section=section)

            attendance_data = []
            for student in students:
                data = {
                    
                    'roll_no': student.roll_no,
                    'student_name': student.name,
                    'batch': student.batch,
                    'attendance': student.attendance
                }
                attendance_data.append(data)

            response_data = {
                'faculty_name': section.faculty , # Add the faculty name to the response
                'attendance_data': attendance_data
                
            }

            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'No section found for the given exam and class.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def get_exam_names(request):
    if request.method == 'GET':
        exam_names = ExamId.objects.values_list('examname', flat=True)
        exam_details = []

        for exam_name in exam_names:
            # Extract exam name
            exam_match = re.match(r"([^\(\-\d]+)\s?(\d+)?", exam_name)
            if exam_match:
                exam = exam_match.group(1).strip()
            else:
                exam = ""

            # Extract date
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", exam_name)
            if date_match:
                date = date_match.group(1)
            else:
                date = ""

            # Extract time
            time_match = re.search(r"\((\w+)\)$", exam_name)
            if time_match:
                time = time_match.group(1)
            else:
                time = ""

            # Retrieve the corresponding ExamId object
            exam_id_obj = ExamId.objects.filter(examname=exam_name).first()
            if exam_id_obj:
                exam_id = exam_id_obj.id
            else:
                exam_id = None

            exam_details.append({
                "exam_id": exam_id,
                "exam_name": exam,
                "date": date,
                "time": time
            })
        return JsonResponse({'exam_details': exam_details})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
@csrf_exempt
def delete_exam(request, exam_id):
    try:
        exam = ExamId.objects.get(id=exam_id)
        exam.delete()
        return JsonResponse({'message': 'Exam and related tables deleted successfully.'})
    except ExamId.DoesNotExist:
        return JsonResponse({'error': 'Exam does not exist.'}, status=404)
    
@csrf_exempt
def get_exam_names_new(request):
    exams = ExamId.objects.all().values('exam_id', 'examname')
    return JsonResponse(list(exams), safe=False)