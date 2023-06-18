from django.urls import path
from . import views

urlpatterns = [
    path('invigilator/get_examnames/<str:facultyname>/', views.get_examnames, name='get_examnames'),
    path('invigilator/get_attendance/<str:exam_name>/<str:faculty_name>/', views.get_attendance, name='get_attendance'),
    path('invigilator/submit_attendance/<str:selected_exam>/', views.submit_attendance, name='submit_attendance'),
    path('invigilator/malpractice/get_roll/<str:section_id>/', views.get_roll, name='get_roll'),
]