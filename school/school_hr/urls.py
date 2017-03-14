from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^holiday/$', views.holiday, name='holiday'),
    url(r'^newstudentprofile/$', views.registerStudent, name='new_student_profile'),
    url(r'^newteacherprofile/$', views.registerTeacher, name='new_teacher_profile'),
    url(r'^leavetype/$', views.add_data, {'input_type': 'Leave Type'}, name='new_leave_type'),
    url(r'^staffcadre/$', views.add_data, {'input_type': 'Staff Cadre'}, name='new_staff_cadre'),
    url(r'^linkcadreteacher/$', views.link_staff_teachers, name='link_cadre_teacher'),
    url(r'^linkleavetype/$', views.link_leave, name='link_leave_type'),
    url(r'^individualattendance/$', views.individual_attendance, name='individual_attendance'),
    url(r'^markedalready/$', views.marked_already, name='marked_already'),
    url(r'^applyleave/$', views.apply_leave, name='apply_leave'),
    url(r'^attendanceapproval/$', views.attendance_approval, name='attendance_approval'),
	# url(r'^teacherattendancerecord/$', views.attendance_employee, {'input_type': 'Teacher'}, name='new_teacher_attendance'),    
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^housedetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
]