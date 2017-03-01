from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render

from school.user_util import user_passes_test_custom
from school_user.models import User, Tenant
from school_student.models import Student
from school_eduadmin.models import total_period,period,classstudent, classteacher, Syllabus, class_section
from school_genadmin.models import academic_year
from school_classadmin.models import Attendance
from .student_parent_view_control import *

@login_required
@user_passes_test_custom(allow_student, redirect_namespace='permission_denied')
#This shall be students view & parents view. Not adminview
def routine(request):
	extension="base_student.html"
	this_tenant=request.user.tenant
	response_data=[]
	current_year=academic_year.objects.filter(tenant=this_tenant).get(current_academic_year=True).year
	student=Student.objects.get(user=request.user)
	current_class=classstudent.objects.for_tenant(this_tenant).filter(year=current_year).get(student=student).class_section
	totalperiod=total_period.objects.get(tenant=this_tenant).number_period
	try:
		perioddata=period.objects.filter(year=current_year, class_section=current_class).select_related('subject', 'teacher')
		for item in perioddata:
			response_data.append({'data_type':'Period','day': item.day,'period': item.period,\
				'subject': item.subject.name, 'teacher':item.teacher.first_name+" "+item.teacher.last_name})
		jsondata=json.dumps(response_data)
		return render (request, 'studentview/routine.html', {'totalperiod': totalperiod, 'class_selected': current_class, \
			'range':range(totalperiod),'user_type':"Student", "extension":extension,"periods":jsondata})
	except:
		return render (request, 'studentview/routine.html', {'totalperiod': totalperiod,'class_selected': current_class, \
			'range':range(totalperiod),'user_type':"Student", "extension":extension})


@login_required
@user_passes_test_custom(allow_student, redirect_namespace='permission_denied')
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
	return render (request, 'studentview/syllabus.html', {'class_selected': current_class, "syllabus":syllabus,\
			'user_type':"Student", "extension":extension, 'ct':ct_name})
	# except:
	# 	return render (request, 'studentview/syllabus.html', {'class_selected': current_class, \
	# 		'user_type':"Student", "extension":extension, 'ct':ct_name})


@login_required
@user_passes_test_custom(allow_student, redirect_namespace='permission_denied')
#This shall be students view & parents view. Not adminview
def apply_leave(request):
	extension="base_student.html"
	this_tenant=request.user.tenant
	if request.method == 'POST':
		response_data=[]
		date=request.POST.get('date')
		remarks=request.POST.get('remarks')
		if (remarks != ''):
			current_year=academic_year.objects.filter(tenant=this_tenant).get(current_academic_year=True).year
			student=Student.objects.get(user=request.user)
			current_classid=classstudent.objects.for_tenant(this_tenant).filter(year=current_year).get(student=student).class_section.id
			current_class_section=class_section.objects.get(id=current_classid)
			attendance_data=Attendance()
			attendance_data.class_section=current_class_section
			attendance_data.student=Student.objects.get(user=request.user)
			attendance_data.has_applied_leave=True
			attendance_data.date=date
			attendance_data.ispresent=False
			attendance_data.student_remarks=remarks
			attendance_data.tenant=this_tenant
			attendance_data.save()
			return HttpResponse(json.dumps(response_data))
		attendance_data.remarks
	return render (request, 'studentview/apply_leave.html', {"extension":extension})

