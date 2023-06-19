from django.urls import re_path,path
from malpractice import views

urlpatterns=[
    re_path(r'^malpractice$',views.malpracticeapi),
    re_path(r'^malpractice/([0-9]+)$',views.malpracticeapi),
    path('malpractice/get_roll/<str:section_id>/', views.get_roll, name='get_roll'),
    path('malpractice/report/<str:section_id>/<str:roll_no>/',views.report,name="report"),

]