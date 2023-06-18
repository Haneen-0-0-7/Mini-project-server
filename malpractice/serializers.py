from rest_framework import serializers
from malpractice.models import malpractice

class malpracticeSerializer(serializers.ModelSerializer):
    class Meta:
        model=malpractice
        fields=('StudentId','StudentRegister',
                'StudentInvigilator','StudentRemark')