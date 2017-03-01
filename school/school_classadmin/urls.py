from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^dailyattendance/$', views.attendance_new, name='dailyattendance_entry'),
    url(r'^editattendance/$', views.attendance_edit, name='editattendance_entry'),
    url(r'^newexamreport/$', views.new_exam_report, name='new_exam_report'),
    url(r'^attendanceview/$', views.attendance_view, name='attendance_view'),
    url(r'^viewexamreport/$', views.exam_report_view, name='exam_report_view'),
    url(r'^viewtranscript/$', views.generate_transcript, name='view_transcript'),
    url(r'^studentlist/$', views.class_students_list, name='student_list'),
    url(r'^studentattendance/$', views.view_student_attendance, name='student_attendance'),
    #url(r'^classdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^calender/$', views.calender, name='calender'),
]