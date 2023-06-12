from django.contrib import admin
from . models import Section
from .models import ExamId
from .models import Batch
# Register your models here.
admin.site.register(ExamId)
admin.site.register(Batch)
admin.site.register(Section)
