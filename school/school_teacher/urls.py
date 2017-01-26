from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^newteacher/$', views.teacherprofile_new, {'input_type': 'Teacher'}, name='new_teacher'),
    url(r'^base/$', views.teacher_base,name='base'),
    url(r'^profilebase/$', views.teacher_student_base,name='profile_base'),
    url(r'^teacherlist/$', views.teacher_list,  name='teacher_list'),
]