from django.urls import re_path
from login import views

urlpatterns=[
    re_path(r'^faculty$',views.facultyapi),
    re_path(r'^faculty/([0-9]+)$',views.facultyapi),
    re_path(r'^faculty/login$', views.faculty_login, name='faculty_login')
]