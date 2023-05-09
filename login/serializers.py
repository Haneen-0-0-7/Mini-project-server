from rest_framework import serializers
from login.models import Faculty

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model=Faculty
        fields=('FacultyId','FacultyName','FacultyPass','FacultyEmail')