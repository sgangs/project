from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    # url(r'^base/$', views.base, name='base'),
    url(r'^monthlysalarystructure/$', views.salary_structure_creation, {'input_type': 'Monthly'}, name='new_monthly_salary'),
    url(r'^epfepssalarystructure/$', views.epf_eps_structure_creation, name='new_epsepf_salary'),
    url(r'^esisalarystructure/$', views.esi_structure_creation, name='new_esier_salary'),
    url(r'^edliadminsalarystructure/$', views.edli_admin_structure_creation, name='new_edli_salary'),
    url(r'^epfemployeestructure/$', views.epf_employee_creation, name='new_epfee_salary'),
    url(r'^esiemployeestructure/$', views.esi_employee_creation, name='new_esiee_salary'),
    url(r'^salarygeneration/$', views.salary_generation, name='new_salary_generation'),
    url(r'^cadreteachersalarylink/$', views.cadre_teacher_salary_linking, name='cadre_salary_link'),
    #url(r'^classdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    #url(r'^calender/$', views.calender, name='calender'),
]