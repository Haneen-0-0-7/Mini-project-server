from django.urls import re_path
from setexam import views

urlpatterns=[
    re_path(r'^setexam/get_exam_details$',views.get_exam_details),
    re_path(r'^setexam/get_exam_details/examname$',views.get_exam_names),
    re_path(r'^setexam/upload_csv$',views.upload_csv),
    re_path(r'^setexam/upload_csv/allotment$',views.classallotment),
    re_path(r'^setexam/get_exam_details/(?P<id>\d+)/$', views.get_exam_details_front),

    # re_path(r'^setexam/get_exam_details/<str:id>/', views.get_exam_details_front),
]