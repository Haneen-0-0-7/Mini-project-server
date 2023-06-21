from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import  Batch
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
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
# from .models import ClassAllotted
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
            
            df = pd.read_csv(csv_file)
            print(df)
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


#Mereena code
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


#Openai code
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
def display(request,examid):
        if request.method == 'GET':
            try:
             print(examid)
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
            print(f'The exam_id is: {exam_id}')

            exam = get_object_or_404(ExamId, exam_id=exam_id)
            print(exam)

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
                            print(branch_name)
                            branch_files[year_folder][branch_name] = os.path.join(year_path, branch_file)
                    print("1.->",branch_files)


            # Allotment logic
            class_count = 1
            allotted_data = []
            leftover_students = []

            for year, branches in branch_files.items():
                for branch_name, branch_file_path in branches.items():
                    print(branch_name)
                    print(branch_file_path)
                    data = []

                    with open(branch_file_path, 'r') as csv_file:
                        csv_reader = csv.reader(csv_file)

                        next(csv_reader)
                        # csv_reader.next()
                        for row in csv_reader:
                            roll_no = row[1]
                            print(roll_no)
                            name = row[2]
                            batch = roll_no[:5]
                            data.append((roll_no, name, batch))
                        

                    allotted_data += data
                    print(allotted_data)

            random.shuffle(allotted_data)
            
            allotted_folder = os.path.join('allotted', exam_id)
            os.makedirs(allotted_folder, exist_ok=True)
            remaining_students = len(allotted_data)
            total_seats = 45  # Total seats available in each class

            while remaining_students > 0:
                print('Normal filling')
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
                    print(leftover_students)
                    continue

                class_seats = np.empty((5, 9), dtype=object)
                class_seats.fill(None)
                
                # Allocate students to seats
                student_objs = []  # Store student objects for later assignment of classid

                # Allocate students to seats
                for i, student in enumerate(class_students):
                    seat_row = i // 9  # Rows 0, 1, 2, 3, 4
                    seat_column = i % 9  # Columns 0, 1, 2, 3, ..., 8
                    roll_no, name, batch = student
                    class_seats[seat_row, seat_column] = roll_no

                    student_obj = Student.objects.create(
                        roll_no=roll_no,
                        name=name,
                        batch=batch,
                        examid=exam,  
                        seat_row=seat_row,
                        seat_column=seat_column
                    )
                    student_objs.append(student_obj)

                
                csv_output_path = os.path.join(allotted_folder, f'class_{class_count}_seats.csv')
                # Create and save the Section object
                section = Section.objects.create(examid= exam, seats=json.dumps(class_seats.tolist()),file_path=csv_output_path)

                # Assign the section id to all the students
                for student_obj in student_objs:
                    student_obj.section = section
                    student_obj.save()
                
                
                # Write class_seats ndarray to CSV file
                with open(csv_output_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(class_seats.tolist())
                
                class_count += 1

            # Allot the leftover students
            if leftover_students:
                num_leftover_students = len(leftover_students)
                print("1->leftover",num_leftover_students,end="/n")
                num_remaining_seats = total_seats - num_leftover_students
                class_seats = np.empty((5, 9), dtype=object)
                class_seats.fill(None)
                std_obj = []
                # Allocate leftover students to seats
                for i, student in enumerate(leftover_students):
                    seat_row = i // num_remaining_seats  # Rows 0, 1, 2, 3, 4
                    seat_column = i % num_remaining_seats  # Columns 0, 1, 2, 3, ..., num_remaining_seats-1
                    roll_no, name, batch = student
                    class_seats[seat_row, seat_column] =  roll_no    

                    student_obj = Student.objects.create(
                        roll_no=roll_no,
                        name=name,
                        batch=batch,
                        examid=exam,
                        seat_row=seat_row,
                        seat_column=seat_column
                    )
                    std_obj.append(student_obj)



                # Create and save the Section object for leftover students
                csv_output_path = os.path.join(allotted_folder, f'class_{class_count}_seats.csv')
                section = Section.objects.create( examid= exam, seats=json.dumps(class_seats.tolist()),file_path=csv_output_path)
                # Write class_seats ndarray to CSV file
                with open(csv_output_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(class_seats.tolist())
                
                # Assign the section id to all the leftover students
                for student_obj in std_obj:
                    student_obj.section = section
                    student_obj.save()
                

            return JsonResponse({'message': 'Allotment process completed successfully.'})

        except Exception as e:
            return JsonResponse({'error': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method.'})




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
        print(form_data)
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
            print(exam_id)
            examname = exam_id.examname
            print(examname)

            # Send email to the faculty
            subject = 'Attendance Notification'
            html_content = render_to_string('attendance_email.html', {'faculty_name': faculty_name, 'class_allotted': class_allotted})
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(subject, text_content, to=[faculty_email])
            email.attach_alternative(html_content, 'text/html')

            # Attach the CSV file to the email
            csv_file_path = section.file_path
            csv_file_name = 'attendance.csv'  # Provide a desired name for the CSV file
            with open(csv_file_path, 'rb') as csv_file:
                email.attach(csv_file_name, csv_file.read(), 'text/csv')

            email.send()

            
            
            print("Class ID:", class_id)
            print("Faculty Name:", faculty_name)
            print("Class Allotted:", class_allotted)
            # Print the faculty email
            print("Faculty Email:", faculty_email)
            print("----------------------")



        
        return JsonResponse({'message': 'Form data processed successfully.'})
    else:
        return JsonResponse({'message': 'Invalid request method.'})
    



@csrf_exempt
def get_classnames(request, exam_name):
    if request.method == 'GET':
        sections = Section.objects.filter(examid__examname=exam_name)
        print(sections)
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

            return JsonResponse({'attendance_data': attendance_data})
        else:
            return JsonResponse({'error': 'No section found for the given exam and class.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    


# @csrf_exempt
# def allotment(request):
#     if request.method == 'POST':
#         try:
#             payload = json.loads(request.body)
#             exam_id = payload.get('examId')
#             print(f'The exam_id is: {exam_id}')

#             batches = Batch.objects.filter(examid__exam_id=exam_id)
#             print(batches)
#             branch_names = []
#             students = []
            
#             for batch in batches:
#                 branch_names.append(batch.branch_name)
#                 file_path = batch.csv_file_path.path

#                 with open(file_path, 'r') as csvfile:
#                     reader = csv.reader(csvfile)
#                     next(reader)  # Skip the header row
                    
#                     for row in reader:
#                         roll_no = row[0]
#                         name = row[1]
#                         batch_name = batch.year + ' ' + batch.branch_name

#                         student = Student.objects.create(
#                             roll_no=roll_no,
#                             name=name,
#                             batch=batch_name,
#                             examid=batch.examid,
#                             seat_row=0,
#                             seat_column=0,
#                             attendance=False
#                         )
#                         students.append(student)
                    
                
            
            



    #     except Exception as e:
    #         return JsonResponse({'error': str(e)}, status=400)
        
    # else:
    #     return JsonResponse({'error': 'Invalid request method.'}, status=400)




import re

@csrf_exempt
def get_exam_names(request):
    if request.method == 'GET':
        exam_names = ExamId.objects.values_list('examname', flat=True)
        exam_details = []

        for exam_name in exam_names:
            # Extract exam name
            exam_match = re.match(r"([^\(\-\d]+)", exam_name)
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
def allotment(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            exam_id = payload.get('examId')
            examid_object = ExamId.objects.get(exam_id = exam_id)
            print(f'The exam_id is: {examid_object}')

            # Retrieve batches for the exam_id
            batch_objects = Batch.objects.filter(examid=examid_object)
            # print(batch_objects)

            # Process the files and create Student objects
            students_list, branch_students_list = process_files(batch_objects)
            

            # Initialize counters and lists
            batch_index = 0
            selected_students = []
            remaining_students = []
            x = "hello"
            while len(students_list) > 0:
                # print("1->",x)
                # Select 25 students from the current batch
                if len(branch_students_list[batch_index]) >= 25:
                    # print("2->",x)
                    current_batch_students = branch_students_list[batch_index][:25]
                    selected_students.extend(current_batch_students[:25])
                    # print(selected_students)
                else:
                    # print("3->",x)
                    remaining_students.extend(branch_students_list[batch_index])
                
                    
                # Delete selected students from students_list
                students_list = [student for student in students_list if student not in current_batch_students]
                # Remove selected students from the current batch in branch_students_list
                branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in current_batch_students]

                # Delete remaining students from students_list
                students_list = [student for student in students_list if student not in remaining_students]

                # Remove remaining students from the current batch in branch_students_list
                branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in remaining_students]

                # Switch to the next batch index in a cyclic manner
                batch_index = (batch_index + 1) % len(branch_students_list)
                # print(batch_index)
                # Select 20 students from the next batch
                if len(branch_students_list[batch_index][:20]) >= 20:
                    # print("4->",x)
                    next_batch_students = branch_students_list[batch_index][:20]
                    selected_students.extend(next_batch_students[:20])
                    # print(selected_students)
    
                else:        
                    # print("5->",x)    
                    remaining_students.extend(branch_students_list[batch_index][:20])
                
                    
    
                # Delete selected students from students_list
                students_list = [student for student in students_list if student not in next_batch_students]

                # Remove selected students from the next batch in branch_students_list
                branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in next_batch_students]

                # Delete remaining students from students_list
                students_list = [student for student in students_list if student not in remaining_students]

                # Remove remaining students from the current batch in branch_students_list
                branch_students_list[batch_index] = [student for student in branch_students_list[batch_index] if student not in remaining_students]

                # Allotment
                class_seats = allot(current_batch_students,next_batch_students )
                # print(class_seats)

                # Switch to the next batch index in a cyclic manner
                batch_index = (batch_index + 1) % len(branch_students_list)
                # print(batch_index)

            return JsonResponse({'message': 'Allotment completed successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)


def process_files(batch_objects):
    students = []
    branch_names = []
    branch_students = []

    for batch in batch_objects:
        branch_names.append(batch.branch_name)
        file_path = batch.csv_file_path.path

        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            branch_students.append([])  # Create an empty list for each branch

            for row in reader:
                roll_no = row[0]
                name = row[1]
                batch_name = batch.year + ' ' + batch.branch_name

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


def allot(first_batch_students, second_batch_students):
    y = "hi"
    # print('Inside allot function')
    class_seats = np.empty((5, 9), dtype=object)
    class_seats.fill(None)
    # print("1->",y)
    current_row = 0
    even_columns = [i for i in range(0, 9, 2)]
    # print(even_columns)
    odd_columns = [i for i in range(1, 9, 2)]
    # print(odd_columns)

    for i, student in enumerate(first_batch_students):
        # print("2->",y)
        # print("i->",i)
        row = current_row
        # print(row)
        col = even_columns[i % len(even_columns)]
        # print(col)
        class_seats[row, col] = student
         # Check if we have filled all the seats in the current row
        if (i + 1) % 5 == 0:
            current_row += 1  # Move to the next row

            # Reset the column index to 0
            if current_row < 5:
                col = even_columns[0]
            else:
                break  # Exit the loop if all rows are filled
            # print("Moving to next row")


    current_row = 0
    for i, student in enumerate(second_batch_students):
        # print("3->", y)
        row = current_row
        col = odd_columns[i % len(odd_columns)]
        class_seats[row, col] = student

        if (i + 1) % 5 == 0:
            current_row += 1
            if current_row < 5:
                col = odd_columns[0]
            else:
                break

        # print("Moving to the next row")

    # Loop to print the entire matrix with student roll numbers
    for row in class_seats:
        for seat in row:
            if seat is None:
                print("Empty", end="\t")
            else:
                roll_number = seat['name']
                print(roll_number, end="\t")
        print()




    return class_seats



