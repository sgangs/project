from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    #url(r'^landing/$', views.genadmin_new, name='landing'),
    url(r'^base/$', views.base, name='base'),
    url(r'^newsubject/$', views.genadmin_new, {'input_type': 'Subject'}, name='new_subject'),
    url(r'^newacademicyear/$', views.genadmin_new, {'input_type': 'Academic Year'}, name='new_academic_year'),
    url(r'^academicyear/$', views.academic_year_data, name='academic_year'),
    url(r'^subject/$', views.subject_data, name='subject_data'),
    url(r'^newclassgroup/$', views.genadmin_new, {'input_type': 'Class Group'}, name='new_class_group'),
    url(r'^newhouse/$', views.genadmin_new, {'input_type': 'House'}, name='new_house'),
    url(r'^newbatch/$', views.genadmin_new, {'input_type': 'Batch'}, name='new_batch'),
    url(r'^newnotice/$', views.genadmin_new, {'input_type': 'Notice'}, name='new_notice'),
    url(r'^calendar/$', views.calendar, name='calendar'),
    url(r'^deletenotice/$', views.notice_event_delete, {'calltype': 'Notice'}, name='notice_delete'),
    url(r'^deleteevent/$', views.notice_event_delete, {'calltype': 'Event'}, name='event_delete'),
    # url(r'^deleteevent/$', views.genadmin_new, {'input_type': 'Notice'}, name='new_notice'),
    url(r'^subjectlist/$', views.master_list, {'input_type': 'Subject'}, name='subject_list'),
    url(r'^classgrouplist/$', views.master_list, {'input_type': 'Class Group'}, name='class_group_list'),
    url(r'^classgrouprename/$', views.change_class_name, name='change_class_name'),
    # url(r'^changeacademicyear/$', views.change_academic_year, name='change_academic_year'),
    url(r'^houselist/$', views.master_list, {'input_type': 'House'}, name='house_list'),
    url(r'^eventlist/$', views.calendar_list, name='event_list'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^housedetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),    
]