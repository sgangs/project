from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^newstudent/$', views.studentprofile_new, {'input_type': 'Student'}, name='new_student'),
    url(r'^newguardian/$', views.studentprofile_new, {'input_type': 'Guardian'}, name='new_guardian'),
    url(r'^neweducation/$', views.studentprofile_new, {'input_type': 'Education'}, name='new_education'),
    url(r'^studentlist/$', views.student_list_paginator, name='student_list'),
    url(r'^editstudent/$', views.student_edit, name='student_edit'),
    url(r'^exportstudentlist/$', views.student_export, name='export_student_list'),
    url(r'^studentimportformat/$', views.student_import_format, name='student_import_format'),
    url(r'^import/', views.import_student, name="studet_import"),
]