from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    # url(r'^newstudentprofile/$', views.registerStudent, name='new_student_profile'),
    # url(r'^newteacherprofile/$', views.registerTeacher, name='new_teacher_profile'),
    url(r'^leavetype/$', views.add_leave, {'input_type': 'Leave Type'}, name='new_leave_type'),
	url(r'^teacherattendancerecord/$', views.attendance_employee, {'input_type': 'Teacher'}, name='new_teacher_attendance'),    
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^housedetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
]