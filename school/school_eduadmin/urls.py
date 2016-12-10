from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^newclass/$', views.class_new, name='new_house'),
    url(r'^newsyllabus/$', views.eduadmin_new, {'input_type': 'Syllabus'}, name='new_house'),
    url(r'^newexam/$', views.eduadmin_new, {'input_type': 'Exam'}, name='new_exam'),
    url(r'^newclassteacher/$', views.eduadmin_new, {'input_type': 'ClassTeacher'}, name='new_classteacher'),
    url(r'^newexaminer/$', views.examiner_new, name='new_examiner'),
    #url(r'^calender/$', views.calender, name='calender'),
]