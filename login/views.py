from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.core.mail import send_mail
from login.models import Faculty
from login.serializers import FacultySerializer
# Create your views here.


@csrf_exempt
def faculty_login(request):
    if request.method == 'POST':
        faculty_data=JSONParser().parse(request)
        username = faculty_data['FacultyName'] 
        password = faculty_data['FacultyPass']
        print('username:', username)
        print('password:', password)
        try:
            faculty = Faculty.objects.get(FacultyName=username, FacultyPass=password)
            print('user:', faculty)
            if faculty is not None:
                response =  JsonResponse({'success':True})
                return response
            else:
                return JsonResponse({'success':False})
        except Faculty.DoesNotExist:
            return JsonResponse({'success':False})
    else:
        return JsonResponse({'success':False})

@csrf_exempt
def facultyapi(request,id=0):
    if request.method=='GET':
        facultys = Faculty.objects.all()
        faculty_serializer = FacultySerializer(facultys,many=True)
        return JsonResponse(faculty_serializer.data,safe=False)
    elif request.method=='POST':
        faculty_data=JSONParser().parse(request)
        faculty_serializer = FacultySerializer(data=faculty_data)
        if faculty_serializer.is_valid():
            faculty_serializer.save()
            subject = 'New Faculty Added'
            username = faculty_data['FacultyName'] 
            password = faculty_data['FacultyPass']
            email = faculty_data['FacultyEmail']
            message = 'Dear Faculty,\n\nYour account has been created with the following credentials:\nUsername: {}\nPassword: {}\n\nPlease use this information to login to your account.\n\nBest regards,\nThe Administration Team'.format(username, password)
            from_email = 'haneenaranhikkalfaheem@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return JsonResponse("Added Successfully",safe=False)
        return JsonResponse("Failed to Add Try another username!!",safe=False)
    elif request.method=='PUT':
        faculty_data=JSONParser().parse(request)
        faculty = Faculty.objects.get(FacultyId=faculty_data['FacultyId'])
        faculty_serializer=FacultySerializer(faculty,data=faculty_data)
        if faculty_serializer.is_valid():
            faculty_serializer.save()
            return JsonResponse("Update Successfully",safe=False)
        return JsonResponse("Failed to Update")

    elif request.method=='DELETE':
        faculty = Faculty.objects.get(FacultyId=id)
        faculty.delete()
        return JsonResponse("Deleted Successfully",safe=False)
    
        