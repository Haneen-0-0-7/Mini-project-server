from rest_framework import serializers
from login.serializers import FacultySerializer
from setexam.models import Allotment

class AllotmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer()

    class Meta:
        model = Allotment
        fields = ['students', 'faculty', 'class_alloted']