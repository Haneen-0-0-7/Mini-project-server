from django.urls import re_path,path
from setexam import views

urlpatterns=[
    re_path(r'^setexam/get_exam_details$',views.get_exam_details),
    re_path(r'^setexam/get_exam_details/examname$',views.get_exam_names),
    re_path(r'^setexam/upload_csv$',views.upload_csv),
    re_path(r'^setexam/upload_csv/allotment$',views.classallotment),
    re_path(r'^setexam/get_exam_details/(?P<id>\d+)/$', views.get_exam_details_front),
    # path('setexam/download_seats_csv/<int:class_id>/',views.download_seats_csv, name='download_seats_csv'),
    path('setexam/display_allotment/<int:examid>/',views.display),
    path('setexam/download_seats_csv/<int:class_id>/', views.download_seats_csv, name='download_seats_csv'),
    path('setexam/facultydetails', views.process_form_data, name='process_form_data'),

    # re_path(r'^setexam/get_exam_details/<str:id>/', views.get_exam_details_front),
]