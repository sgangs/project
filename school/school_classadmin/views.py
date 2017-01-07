from datetime import date, datetime
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F
#from .forms import SyllabusForm, ExamForm
from .models import Attendance, exam_report
from .class_admin_support import *
#from school_eduadmin.models import * #class_section
from school_teacher.models import Teacher
from school_student.models import Student
from school_eduadmin.models import classstudent, Exam
from school_genadmin.models import class_group, Subject



@login_required
#This is the base page.
def base(request):
	return render (request, 'classadmin/classadmin_base.html')


@login_required
#This function helps in addidng new attendance. Error 1- Why do we need to import class section for each function??
def attendance_new(request):
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	classes = class_section.objects.for_tenant(request.user.tenant)
	#students=classstudent.objects.for_tenant(request.user.tenant).filter(year__exact=year).student
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		this_tenant=request.user.tenant

		#Getting student details based on selection
		if (calltype == 'details'):
			called_for='Attendance'
			response_data=get_student_data(request, called_for, classes)
		#saving the class
		if (calltype == 'save'):
			classid=request.POST.get('classid')
			year=request.POST.get('year')
			date=request.POST.get('date')
			class_final=classes.get(id__exact=classid)
			student_list=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
			attendance_data = json.loads(request.POST.get('details'))
			for data in attendance_data:
				student_id=data['student_id']
				ispresent=data['is_present']
				remarks=data['remarks']
				#Better still if we could check if student is in that said class for data integrity
				student=Student.objects.get(id=student_id)
				attendance=Attendance()
				attendance.class_section=class_final
				attendance.student=student
				attendance.date=date
				attendance.ispresent=ispresent
				attendance.remarks=remarks
				attendance.tenant=this_tenant
				attendance.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/class_attendance.html', {'items':classes})


@login_required
#This view is for reporting daily class-wsie attendance. Error 1- Why do we need to import class section for each function??
def attendance_view(request):
	from school_eduadmin.models import class_section
	if request.method == 'POST':
		response_data = []
		this_tenant=request.user.tenant
		response_data = get_attendance_data(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	classes = class_section.objects.for_tenant(request.user.tenant)
	return render (request, 'classadmin/attendance_view.html', {'items':classes})


@login_required
#This function helps in addidng exam scores. Error 1- Why do we need to import class section for each function??
def new_exam_report(request):
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	classes = class_section.objects.for_tenant(request.user.tenant)
	exams = Exam.objects.for_tenant(request.user.tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		this_tenant=request.user.tenant
		#Getting subject details based on selection
		if (calltype == 'details'):
			called_for='Exam'
			response_data=get_subject_data(request, called_for, classes)
		#Getting student details based on selection
		if (calltype == 'subject'):
			called_for='Exam'
			response_data=get_student_data(request, called_for, classes)
		#saving the exam report
		elif (calltype == 'save'):
			classid=int(request.POST.get('classid'))
			examid=request.POST.get('examid')
			subjectid=request.POST.get('subjectid')
			class_final=classes.get(id__exact=classid)
			exam=Exam.objects.get(id__exact=examid)
			subject=Subject.objects.get(id__exact=subjectid)
			year=exam.year
			student_list=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
			report_details = json.loads(request.POST.get('details'))
			for data in report_details:
				student_id=data['student_id']
				external_score=int(data['external'])
				internal_score=int(data['internal'])
				final_score=int(data['final'])
				remarks=data['remarks']
				#Better still if we could check if student is in that said class for data integrity
				student=Student.objects.get(id=student_id)
				exam_report_entry=exam_report()
				exam_report_entry.class_section=class_final
				exam_report_entry.exam=exam
				exam_report_entry.subject=subject
				exam_report_entry.student=student				
				exam_report_entry.external_score=external_score
				exam_report_entry.internal_score=internal_score
				exam_report_entry.final_score=final_score
				exam_report_entry.remarks=remarks
				exam_report_entry.tenant=this_tenant
				exam_report_entry.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/new_examreport.html', {'items':classes, 'exams':exams})

#Exam Report View
def exam_report_view(request):
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	classes = class_section.objects.for_tenant(request.user.tenant)
	exams = Exam.objects.for_tenant(request.user.tenant)
	#students=classstudent.objects.for_tenant(request.user.tenant).filter(year__exact=year).student
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		this_tenant=request.user.tenant
		#Getting student details based on selection
		if (calltype == 'details'):
			called_for='Exam'
			response_data=get_subject_data(request, called_for, classes)
		elif (calltype == 'subject'):
			called_for='Exam'
			response_data=get_exam_report(request, called_for, classes)
			#response_data=["Ram"]
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/view_examreport.html', {'items':classes, 'exams':exams})

@login_required
#This function helps in addidng new attendance. Error 1- Why do we need to import class section for each function??
def attendance_edit(request):
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	classes = class_section.objects.for_tenant(request.user.tenant)
	#students=classstudent.objects.for_tenant(request.user.tenant).filter(year__exact=year).student
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		this_tenant=request.user.tenant

		#Getting student details based on selection
		if (calltype == 'details'):
			called_for='Attendance'
			response_data=get_student_data(request, called_for, classes)
		#Getting student details based on selection
		elif (calltype == 'attendance'):
			called_for='Attendance'
			response_data=get_studentattendance_data(request, called_for, classes)
		#saving the class
		if (calltype == 'save'):
			classid=request.POST.get('classid')
			year=request.POST.get('year')
			date=request.POST.get('date')
			class_final=classes.get(id__exact=classid)
			student_list=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
			attendance_data = json.loads(request.POST.get('details'))
			for data in attendance_data:
				student_id=data['student_id']
				ispresent=data['is_present']
				remarks=data['remarks']
				#Better still if we could check if student is in that said class for data integrity
				student=Student.objects.get(id=student_id)
				attendance=Attendance()
				attendance.class_section=class_final
				attendance.student=student
				attendance.date=date
				attendance.ispresent=ispresent
				attendance.remarks=remarks
				attendance.tenant=this_tenant
				attendance.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/class_attendance_edit.html', {'items':classes})