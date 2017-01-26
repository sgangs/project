from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^routine/$', views.routine, name='routine'),
    url(r'^syllabus/$', views.syllabus_view, name='syllabus'),
    #url(r'^classdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^calender/$', views.calender, name='calender'),
]