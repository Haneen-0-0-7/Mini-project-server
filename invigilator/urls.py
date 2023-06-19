from django.urls import path
from . import views

urlpatterns = [
    path('get_examnames/<str:facultyname>/', views.get_examnames, name='get_examnames'),
    path('get_attendance/<str:exam_name>/<str:faculty_name>/', views.get_attendance, name='get_attendance'),
    # path('submit_attendance/',views.submit_attendance,name="submit_attendance"),
    path('submit_attendance/<str:selected_exam>/', views.submit_attendance, name='submit_attendance'),
    

]
