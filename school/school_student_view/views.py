from datetime import datetime
import json
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render

from school_user.models import User, Tenant
from school_student.models import Student
from school_eduadmin.models import total_period,period,classstudent, classteacher, Syllabus
from school_genadmin.models import academic_year

#This shall be students view, parents view & maybe teacher's view. Not adminview
def routine(request):
	extension="base_student.html"
	this_tenant=request.user.tenant
	current_year=academic_year.objects.filter(tenant=this_tenant).get(current_academic_year=True).year
	student=Student.objects.get(user=request.user)
	current_class=classstudent.objects.for_tenant(this_tenant).filter(year=current_year).get(student=student).class_section
	totalperiod=total_period.objects.get(tenant=this_tenant).number_period
	try:
		perioddata=period.objects.filter(year=current_year).get(class_section=current_class)
		return render (request, 'studentview/routine.html', {'totalperiod': totalperiod, 'class_selected': current_class, \
			'range':range(totalperiod),'user_type':"Student", "extension":extension,})
	except:
		return render (request, 'studentview/routine.html', {'totalperiod': totalperiod,'class_selected': current_class, \
			'range':range(totalperiod),'user_type':"Student", "extension":extension})


#This shall be students view & parents view. Not adminview
def syllabus_view(request):
	extension="base_student.html"
	this_tenant=request.user.tenant
	current_year=academic_year.objects.filter(tenant=this_tenant).get(current_academic_year=True).year
	student=Student.objects.get(user=request.user)
	current_class=classstudent.objects.for_tenant(this_tenant).filter(year=current_year).get(student=student).class_section
	ct_first_name=classteacher.objects.get(class_section=current_class,year=current_year).class_teacher.first_name #ct is class teacher
	ct_last_name=classteacher.objects.get(class_section=current_class,year=current_year).class_teacher.last_name #ct is class teacher
	ct_name=ct_first_name +" "+ct_last_name
	classgroup=current_class.classgroup
	# try:
	syllabus=Syllabus.objects.filter(year=current_year,class_group=classgroup).select_related('subject')
	print(syllabus)
	return render (request, 'studentview/syllabus.html', {'class_selected': current_class, "syllabus":syllabus,\
			'user_type':"Student", "extension":extension, 'ct':ct_name})
	# except:
	# 	return render (request, 'studentview/syllabus.html', {'class_selected': current_class, \
	# 		'user_type':"Student", "extension":extension, 'ct':ct_name})








	