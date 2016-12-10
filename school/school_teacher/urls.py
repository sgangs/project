from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^newteacher/$', views.teacherprofile_new, {'input_type': 'Teacher'}, name='new_teacher'),
]