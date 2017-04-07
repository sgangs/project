from datetime import date, datetime
from decimal import Decimal
import json
from dateutil.rrule import *
from dateutil.parser import *
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from school.user_util import user_passes_test_custom
from app_control.view_control import *
from .models import *
from .class_admin_support import *
from school_teacher.models import Teacher
from school_student.models import Student
from school_eduadmin.models import classstudent, Exam, exam_creation, grade_table, grade_item,  classteacher, subject_teacher
from school_genadmin.models import class_group, Subject, annual_calender, academic_year
from school_genadmin.genadmin_util import holiday_calculator



@login_required
#This is the base page.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def base(request):
	return render (request, 'classadmin/classadmin_base.html')


@login_required
#This function helps in getting list of students in school
#We need to check who must have control on this
def class_students_list(request):
	extension='base.html'
	from school_eduadmin.models import class_section
	classes = class_section.objects.for_tenant(request.user.tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		this_tenant=request.user.tenant
		#Getting student details based on selection
		if (calltype == 'details'):
			called_for='Attendance'
			response_data=get_student_data(request, called_for, classes)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/students_list.html', {'items':classes, "extension":extension})

@login_required
@user_passes_test_custom(allow_admin_teacher, redirect_namespace='permission_denied')
#This function helps in addidng new attendance. Error 1- Why do we need to import class section for each function??
def attendance_new(request):
	from school_eduadmin.models import class_section
	this_tenant=request.user.tenant
	acad=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	year=acad.year
	start=acad.start.isoformat()
	end=acad.end.isoformat()
	if (request.user.user_type=='Teacher'):
		teacher=Teacher.objects.get(user=request.user)
		class_teachers=classteacher.objects.for_tenant(this_tenant).filter(year=year, class_teacher=teacher)
		classes = class_section.objects.for_tenant(this_tenant).filter(classteacher_classSection__in=class_teachers)
		extension="base_teacher.html"
	else:
		extension="base.html"
		classes = class_section.objects.for_tenant(this_tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		#Getting student details based on selection
		if (calltype == 'details'):
			called_for='Attendance'
			response_data=get_student_data(request, called_for, classes)
		#saving the class
		elif (calltype == 'save'):
			classid=request.POST.get('classid')
			# year=request.POST.get('year')
			date=request.POST.get('date')
			class_final=classes.get(id__exact=classid)
			#Getting set of student ids for validation
			list_student=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
			students_final=list(Student.objects.filter(classstudent_eduadmin_student_student__in=list_student).values('id'))
			students_set=set()
			for i in students_final:
				for k,v in i.items():
					students_set.add(v)
			attendance_data = json.loads(request.POST.get('details'))
			with transaction.atomic():
				try:
					for data in attendance_data:
						student_id=int(data['student_id'])
						ispresent=data['is_present']
						remarks=data['remarks']
						#If is used to validate whether input student is in student set (of the class selected)
						if (student_id in students_set):
							student=Student.objects.for_tenant(this_tenant).get(id=student_id)
							attendance=Attendance()
							attendance.class_section=class_final
							attendance.student=student
							attendance.date=date
							attendance.ispresent=ispresent
							attendance.remarks=remarks
							attendance.tenant=this_tenant
							attendance.save()
						else:
							raise IntegrityError
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'classadmin/class_attendance.html', {'items':classes, 'min':start, 'max':end, "extension":extension})


@login_required
@user_passes_test_custom(allow_admin_teacher, redirect_namespace='permission_denied')
#This view is for reporting daily class-wsie attendance. Error 1- Why do we need to import class section for each function??
def attendance_view(request):
	from school_eduadmin.models import class_section
	if request.method == 'POST':
		response_data = []
		response_data = get_attendance_data(request)
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	this_tenant=request.user.tenant
	acad=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	year=acad.year
	start=acad.start.isoformat()
	end=acad.end.isoformat()
	if (request.user.user_type=='Teacher'):
		extension="base_teacher.html"
		teacher=Teacher.objects.get(user=request.user)
		class_teachers=classteacher.objects.for_tenant(this_tenant).filter(year=year, class_teacher=teacher)
		subject_teachers=subject_teacher.objects.for_tenant(this_tenant).filter(year=year, teacher=teacher)
		classes = list(class_section.objects.for_tenant(this_tenant).filter(classteacher_classSection__in=class_teachers))
		others = list(class_section.objects.for_tenant(this_tenant).filter(subjectTeacher_classSection__in=subject_teachers))
		for i in others:
			classes.append(i)
		classes=set(classes)
		print(classes)
	else:
		extension="base.html"
		classes = class_section.objects.for_tenant(request.user.tenant)
	return render (request, 'classadmin/attendance_view.html', {'items':classes,'min':start, 'max':end, "extension":extension})


@login_required
#This function helps in addidng exam scores. Error 1- Why do we need to import class section for each function??
def new_exam_report(request):
	extension='base.html'
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	this_tenant=request.user.tenant
	classes = class_section.objects.for_tenant(this_tenant)
	exams = Exam.objects.for_tenant(this_tenant)
	grade_name=grade_table.objects.get(tenant=this_tenant)
	grades=list(grade_item.objects.for_tenant(tenant=this_tenant).filter(grade_table=grade_name).\
			values('min_mark','max_mark','grade','grade_point'))
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
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
			# student_list=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
			report_details = json.loads(request.POST.get('details'))
			for data in report_details:
				student_id=data['student_id']
				grade=data['grade']
				grade_point=Decimal(data['grade_point'])
				final_score=int(data['final'])
				remarks=data['remarks']
				#Better still if we could check if student is in that said class for data integrity
				student=Student.objects.get(id=student_id)
				exam_report_entry=exam_report()
				exam_report_entry.class_section=class_final
				exam_report_entry.exam=exam
				exam_report_entry.subject=subject
				exam_report_entry.student=student				
				exam_report_entry.grade=grade
				exam_report_entry.grade_point=grade_point
				exam_report_entry.final_score=final_score
				exam_report_entry.remarks=remarks
				exam_report_entry.year=exam.year
				exam_report_entry.tenant=this_tenant
				exam_report_entry.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'classadmin/new_examreport.html', {'items':classes, 'exams':exams, \
					'grades':json.dumps(grades,cls=DjangoJSONEncoder), "extension":extension})

def exam_report_edit(request):
	extension='base.html'
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	this_tenant=request.user.tenant
	classes = class_section.objects.for_tenant(this_tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if (calltype == 'details'):
			called_for='Exam'
			response_data=get_subject_data(request, called_for, classes)
		if (calltype == 'subject'):
			response_data=get_exam_marks(request, classes, this_tenant)
			
		#saving the exam report
		elif (calltype == 'save'):
			report_details = json.loads(request.POST.get('details'))
			for data in report_details:
				exam_report_id=data['report_id']
				grade=data['grade']
				grade_point=Decimal(data['grade_point'])
				final_score=int(data['final'])
				remarks=data['remarks']
				exam_report_entry=exam_report.objects.for_tenant(this_tenant).get(id=exam_report_id)
				exam_report_entry.grade=grade
				exam_report_entry.grade_point=grade_point
				exam_report_entry.final_score=final_score
				exam_report_entry.remarks=remarks
				exam_report_entry.save()
		jsondata=json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	current_academic_year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	exams = Exam.objects.for_tenant(request.user.tenant).filter(year=current_academic_year.year)
	grades=list(grade_table.objects.for_tenant(tenant=this_tenant).filter(grade_type='S').\
			values('min_mark','max_mark','grade','grade_point'))
	return render (request, 'classadmin/edit_examreport.html', {'items':classes, 'exams':exams, \
					'grades':json.dumps(grades,cls=DjangoJSONEncoder), "extension":extension})



@login_required
#Exam Report View
def exam_report_view(request):
	extension='base.html'
	from school_eduadmin.models import class_section
	#For the next line, do remember django does lazy querying.
	this_tenant=request.user.tenant
	classes = class_section.objects.for_tenant(this_tenant)
	current_academic_year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	exams = Exam.objects.for_tenant(request.user.tenant).filter(year=current_academic_year.year)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		#Getting student details based on selection
		if (calltype == 'subject'):
			called_for='Exam'
			response_data=get_exam_report(request, called_for, classes)
			#response_data=["Ram"]
			#This is just randomly checking mail
			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/view_examreport_crossfilter.html', {'items':classes, 'exams':exams, "extension":extension})


@login_required
#This function helps in addidng new attendance. Error 1- Why do we need to import class section for each function??
def attendance_edit(request):
	extension='base.html'
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
			# student_list=classstudent.objects.for_tenant(request.user.tenant).filter(class_section=class_final,year=year)
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

	return render (request, 'classadmin/class_attendance_edit.html', {'items':classes, "extension":extension})

@login_required
def view_student_attendance(request):
	extension='base.html'
	this_tenant=request.user.tenant
	students=Student.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		response_data = []
		studentid=request.POST.get('studentid')
		start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d").date()
		end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d").date()
		student=students.get(id=studentid)
		attendance=Attendance.objects.filter(student=student, date__range=(start,end))
		attendace_dates=[]
		for i in attendance:
			attendace_dates.append(datetime.strptime(datetime.strftime(i.date,'%Y %m %d'), '%Y %m %d'))
		total=list(rrule(DAILY, dtstart=start, until=end))
		events= annual_calender.objects.filter(date__range=(start,end))
		events_hol=events.filter(attendance_type=2)
		hol=[]
		for event in events_hol:
			hol.append(datetime.strptime(datetime.strftime(event.date,'%Y %m %d'), '%Y %m %d'))
		hol=holiday_calculator(start, end, events, hol)
		total_working=list(set(total) -set(hol))
		no_rep=list(set(total_working)-set(attendace_dates))
		hol.sort();
		no_rep.sort();
		for i in attendance:
			response_data.append({'data_type':'Report','is_present':i.ispresent, \
				'date': datetime.strftime(i.date, '%d -%m -%Y'), 'remarks':i.remarks})
		for i in no_rep:
			response_data.append({'data_type':'No Report','date': datetime.strftime(i, '%d -%m -%Y')})
		for i in hol:
			response_data.append({'data_type':'Holiday','date': datetime.strftime(i, '%d -%m -%Y')})		
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'classadmin/attendance_view_student.html',{'items':students,"extension":extension})

@login_required
def generate_transcript(request):
	extension='base.html'
	this_tenant=request.user.tenant
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	exam_type=exam_creation.objects.for_tenant(this_tenant).get(year=year).exam_type
	exams=Exam.objects.for_tenant(this_tenant).filter(year=year)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if calltype=='class':
			class_selected = request.POST.get('classsection')
			students_list=classstudent.objects.for_tenant(request.user.tenant).\
				filter(class_section=class_selected,year=year).select_related("student")	
			for student in students_list:
				response_data.append({'data_type':'Student','id':student.student.id,'roll_no': student.roll_no,\
					'first_name': student.student.first_name, 'last_name': student.student.last_name})
		elif calltype=='student':
			#Getting student details based on selection
			# if (exam_type=='CCE'):
			response_data=generate_student_transcript(request, year)
		jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
		return HttpResponse(jsondata)
	classes = class_section.objects.for_tenant(this_tenant)
	# if (exam_type=='CCE'):
	return render (request, 'classadmin/transcript_exam_cce.html', {'items':classes, "extension":extension})
	# else:
		# return render (request, 'classadmin/transcript_exam_generic.html', {'items':classes,'exams':exams, "extension":extension})

