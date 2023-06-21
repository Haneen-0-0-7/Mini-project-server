from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from login.models import Faculty
from setexam.models import Section, ExamId, Student
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def get_examnames(request, facultyname):
    if request.method == 'GET':
        faculty = get_object_or_404(Faculty, FacultyName=facultyname)
        sections = Section.objects.filter(faculty=facultyname)
        unique_exam_ids = sections.values('examid_id').distinct()
        exam_ids = unique_exam_ids.values_list('examid_id', flat=True)
        exam_names = ExamId.objects.filter(id__in=exam_ids).values_list('examname', flat=True)
        exam_names_list = list(exam_names)

        return JsonResponse({'exam_names': exam_names_list})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@csrf_exempt
def get_attendance(request, exam_name, faculty_name):
    if request.method == 'GET':
        section = Section.objects.filter(examid__examname=exam_name, faculty=faculty_name).first()
        if section:
            students = Student.objects.filter(section=section)

            attendance_data = []
            for student in students:
                data = {
                    'student_id': student.id,
                    'roll_no': student.roll_no,
                    'student_name': student.name,
                    'batch': student.batch,
                    'attendance': student.attendance
                }
                attendance_data.append(data)
            response_data = {
                'section_id': section.class_id,
                'attendance_data': attendance_data
            }

           
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'No section found for the given exam and faculty.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
@csrf_exempt
def submit_attendance(request, selected_exam):
    if request.method == "POST":
        payload = json.loads(request.body)
        attendance_data = payload.get('attendance_data', [])
        # Process the attendance_data
        for data in attendance_data:
            student_id = data.get('student_id')
            attendance = data.get('attendance')
            student = get_object_or_404(Student, id=student_id)
            student.attendance = attendance
            student.save()   

        return JsonResponse({"message": "Attendance submitted successfully."})
    else:
        return JsonResponse({"message": "Invalid request method."}, status=400)

@csrf_exempt
def get_roll(request, section_id):
    if request.method == 'GET':
        students = Student.objects.filter(section_id=section_id)
        
        roll_numbers = [student.roll_no for student in students]
        
        return JsonResponse({'roll_numbers': roll_numbers})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)