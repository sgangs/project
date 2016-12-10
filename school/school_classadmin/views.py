from functools import partial, wraps
import json
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F

from .forms import SyllabusForm, ExamForm
from .models import class_section, classteacher
from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import class_group, Subject


@login_required
#This is the class list for taing attendance
def class_list(request):
	class_section=class_section.objects.for_tenant(request.user.tenant)
	return render (request, 'genadmin/calendar.html', {'class_section': input_type})


@login_required
#This is the class list for taing attendance
def class_report(request, class_id, input_type):
	if (input_type == "Attendance"):
		attendance_new(request, class_name)
	#elif (input_type == "Exam Report")
	#	examreport_new(request, class_name)



@login_required
#This function helps in addidng new attendance
def attendance_new(request, class_id):
	date=datetime.now()
	year=date.year
	class_name=class_id.split("-",3)[3]
	class_section=class_section.objects.for_tenant(request.user.tenant).get_object_or_404(name__iexact=class_name)
	class_teacher=Teacher.objects.for_tenant(request.user.tenant)
	students=classstudent.objects.for_tenant(request.user.tenant).filter(year__exact=year).student
	teacher=classteacher.objects.for_tenant(request.user.tenant).filter(year__exact=year).teacher
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant

		#checking classname
		# if (calltype == 'classname'):
		# 	name = request.POST.get('name')
		# 	response_data['name'] = class_section.objects.for_tenant(this_tenant).get(name__iexact=name).name

		#saving the class
		if (calltype == 'save'):
			isdate = request.POST.get('is date?')
			name = request.POST.get('class_name')
			class_section=class_section.objects.for_tenant(request.user.tenant).get_object_or_404(name__iexact=name)
			attendance_data = json.loads(request.POST.get('bill_details'))
			if isdate:
				date = request.POST.get('date')
			else:
				date = date.today()
			for student in attendance_data:
				studentid=data['studentid']
				ispresent=data['ispresent']
				#Better still if we could check if student is in that said class for data integrity
				student=Student.objects.for_tenant(request.user.tenant).get(key__exact=studentid)
				attendance=Attendance()
				attendance.class_section=class_section
				attendance.student=student
				attendance.date=date
				attendance.ispresent=ispresent
				attendance.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/daily_attendance.html', \
					{'students':students,'teacher': class_teacher,'class_section': class_section,})
