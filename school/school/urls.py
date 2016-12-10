from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from school import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view()),
    url(r'^register/$', views.RegisterView, name='register'),
    url(r'^login/', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^landing/$', views.landing, name='landing'),
    url(r'^genadmin/', include('school_genadmin.urls',namespace='genadmin', app_name='genadmin')),
    url(r'^eduadmin/', include('school_eduadmin.urls',namespace='eduadmin', app_name='eduadmin')),
    #url(r'^classadmin/', include('school_classadmin.urls',namespace='classadmin', app_name='classadmin')),
    url(r'^studentprofile/', include('school_student.urls',namespace='student', app_name='student')),
    url(r'^teacherprofile/', include('school_teacher.urls',namespace='teacher', app_name='teacher')),
]