from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from malpractice.models import malpractice
from malpractice.serializers import malpracticeSerializer
# Create your views here.
@csrf_exempt
def malpracticeapi(request,id=0):
    if request.method=='GET':
        malpractices = malpractice.objects.all()
        malpractice_serializer = malpracticeSerializer(malpractices,many=True)
        return JsonResponse(malpractice_serializer.data,safe=False)
    elif request.method=='POST':
        malpractice_data=JSONParser().parse(request)
        malpractice_serializer = malpracticeSerializer(data=malpractice_data)
        if malpractice_serializer.is_valid():
            malpractice_serializer.save()
            return JsonResponse("Record Added Successfully",safe=False)
        return JsonResponse("Failed to Add Check The Register No!!",safe=False)
    elif request.method=='PUT':
        malpractice_data=JSONParser().parse(request)
        try:
           malpractice_obj = malpractice.objects.get(StudentId=malpractice_data['StudentId'])
        except malpractice.DoesNotExist:
           return JsonResponse("Record not found", safe=False)
        malpractice_serializer=malpracticeSerializer(malpractice_obj,data=malpractice_data)
        if malpractice_serializer.is_valid():
           malpractice_serializer.save()
           return JsonResponse("Updated Record Successfully",safe=False)
        if not malpractice_serializer.is_valid():
           print(malpractice_serializer.errors)
        return JsonResponse("Failed to Update",safe=False)

    elif request.method=='DELETE':
        malpractice_obj = malpractice.objects.get(StudentId=id)
        malpractice_obj.delete()
        return JsonResponse("Deleted Successfully",safe=False)