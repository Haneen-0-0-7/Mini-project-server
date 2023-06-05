from django.urls import re_path
from malpractice import views

urlpatterns=[
    re_path(r'^malpractice$',views.malpracticeapi),
    re_path(r'^malpractice/([0-9]+)$',views.malpracticeapi)
]