from django.urls import re_path,path
from setexam import views

urlpatterns=[
    re_path(r'^setexam/get_exam_details$',views.get_exam_details),
    re_path(r'^setexam/get_exam_details/examname$',views.get_exam_names_new),
    re_path(r'^setexam/upload_csv$',views.upload_csv),
    re_path(r'^setexam/upload_csv/allotment$',views.classallotment),
    re_path(r'^setexam/get_exam_details/(?P<id>\d+)/$', views.get_exam_details_front),
    path('setexam/display_allotment/<int:examid>/',views.display),
    path('setexam/download_seats_csv/<int:class_id>/', views.download_seats_csv, name='download_seats_csv'),
    path('setexam/facultydetails', views.process_form_data, name='process_form_data'),
    path('setexam/get_class/<str:exam_name>/',views.get_classnames,name="get_class"),
    path('setexam/get_attendance/<str:exam_name>/<str:class_name>/', views.get_attendance, name='get_attendance'),
    path('setexam/exam-names/', views.get_exam_names, name='get_exam_names'),
    path('setexam/delete/<int:exam_id>/', views.delete_exam, name='delete_exam'),
]