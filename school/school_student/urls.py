from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^newstudent/$', views.studentprofile_new, {'input_type': 'Student'}, name='new_student'),
    url(r'^newguardian/$', views.studentprofile_new, {'input_type': 'Guardian'}, name='new_student'),
    url(r'^neweducation/$', views.studentprofile_new, {'input_type': 'Education'}, name='new_student'),
    url(r'^studentlist/$', views.student_list, name='student_list'),
]