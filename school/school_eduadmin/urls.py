from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^newclass/$', views.class_new, name='new_class'),
    #url(r'^newclassstudent/$', views.class_student_add, name='new_class_student'),
    url(r'^newsyllabus/$', views.eduadmin_new, {'input_type': 'Syllabus'}, name='new_syllabus'),
    url(r'^newexam/$', views.eduadmin_new, {'input_type': 'Exam'}, name='new_exam'),
    url(r'^newclassteacher/$', views.eduadmin_new, {'input_type': 'ClassTeacher'}, name='new_classteacher'),
    url(r'^newsubjectteacher/$', views.eduadmin_new, {'input_type': 'Subject Teacher'}, name='new_subject_teacher'),
    url(r'^newclassstudent/$', views.eduadmin_new, {'input_type': 'ClassStudent'}, name='new_class_student'),
    url(r'^newexaminer/$', views.eduadmin_new, {'input_type': 'Examiner'}, name='new_examiner'),
    url(r'^totalperiodentry/$', views.eduadmin_new, {'input_type': 'Total Period'}, name='total_period_entry'),
    url(r'^classlist/$', views.eduadmin_list, {'input_type': 'Class'}, name='class_list'),
    url(r'^subjectteacherlist/$', views.eduadmin_list, {'input_type': 'Subject Teacher'}, name='subject_teacher_list'),
    url(r'^classdetail/(?P<detail>[-\S]+)/addperiod/$', views.period, name='add_period'),
    url(r'^classdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
    #url(r'^calender/$', views.calender, name='calender'),
]