from functools import partial, wraps
from itertools import chain
import json
#from datetime import datetime
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F

from school.user_util import user_passes_test_custom
from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import class_group, Subject, Batch, academic_year
from school_fees.models import student_fee, group_default_fee
from .forms import *
from .models import *
from .eduadmin_util import *
from app_control.view_control import *

@login_required
#This is the base page.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def base(request):
	return render (request, 'eduadmin/eduadmin_base.html')


@login_required
#This function helps in creating new class
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def class_new(request):
	#date=datetime.now()
	this_tenant=request.user.tenant
	group=class_group.objects.for_tenant(this_tenant)
	class_teacher=Teacher.objects.for_tenant(this_tenant).filter(staff_type="Teacher").all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		#saving the class
		if (calltype == 'classname'):
			classname = request.POST.get('classname')
			try:
				objecgt_sucess = class_section.objects.for_tenant(this_tenant).get(name__iexact=classname)
				response_data['name'] = "Class Exist"
			except:
				ObjectDoesNotExist

		elif (calltype == 'save'):
			with transaction.atomic():
				try:
					group=request.POST.get('classgroup')
					name = request.POST.get('classname')
					room=request.POST.get('room')
					teacher_key=request.POST.get('classteacher')
					year=request.POST.get('year')
					teacher_added=request.POST.get('teacher_added')
					section=class_section()
					section.name=name
					section.room=room
					section.classgroup=class_group.objects.for_tenant(request.user.tenant).get(name__iexact=group)
					section.tenant=this_tenant
					section.save()
					if (teacher_added == "true"):
						teacher=classteacher()
						teacher.class_section=section
						teacher.class_teacher=Teacher.objects.for_tenant(request.user.tenant).\
							get(staff_type="Teacher",key__exact=teacher_key)
						teacher.year=year
						teacher.tenant=this_tenant
						teacher.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'eduadmin/new_class.html', {'groups':group,'teachers': class_teacher})
	
@login_required
#This function helps in addidng new syllabus and exams
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def eduadmin_new(request, input_type):
	if (input_type=="Syllabus"):
		importform=SyllabusForm
		name='eduadmin:class_list'
	elif (input_type=="Exam"):
		importform=ExamForm
		name='eduadmin:class_list'
	elif (input_type=="ClassTeacher"):
		importform=ClassTeacherForm
		name='eduadmin:class_list'
	elif (input_type=="ClassStudent"):
		importform=ClassStudentForm
		name='eduadmin:class_list'
		input_type="Student (one at a time) To Class"
	elif (input_type=="Subject Teacher"):
		importform=SubjectTeacherForm
		name='eduadmin:subject_teacher_list'
	elif (input_type=="Total Period"):
		importform=TotalPeriodForm
		name='eduadmin:class_list'
	elif (input_type=="Term"):
		importform=TermForm
		name='eduadmin:base'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	#importformset=formset_factory(wraps(importform)(partial(importform, tenant=current_tenant)), extra=3)
	#formset=importformset()
	#helper=ManufacturerFormSetHelper()
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		#form = formset(request.POST, tenant=current_tenant)
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			if (input_type=="ClassStudent"):
				with transaction.atomic():
					try:
						item.save()
						try:
							fee=student_fee()
							fee.student=item.student
							class_section=item.class_section
							classgroup=class_section.classgroup
							year=item.year
							fee_group=group_default_fee.objects.get(classgroup=classgroup,year=year)
							yearly_fee=fee_group.yearly_fee.all()
							monthly_fee=fee_group.monthly_fee
							fee.monthly_fee=monthly_fee
							fee.year=year
							fee.tenant=current_tenant
							fee.save()
							for data in yearly_fee:
								fee.yearly_fee.add(data)
						except:
							pass
					except:
						transaction.rollback()
			else:
				item.save()
			return redirect(name)
	#else:
	#	form=importform(tenant=request.user.tenant)	
	#return render(request, 'master/new.html',{'formset': formset, 'helper': helper, 'item': type})
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})


@login_required
#This is used to add subject teachers.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def subject_teacher_new(request):
	class_section_option=class_section.objects.for_tenant(request.user.tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		if (calltype == 'class_selection'):
			class_name=request.POST.get('class_name')
			classgroup=class_section.get_object_or_404(name=class_name).classgroup
			subject_options=Syllabus.objects.for_tenant(request.user.tenant).filter(class_group=classgroup).subject
			response_data['subjects'] = subject_options
		elif (calltype == 'subject_selection'):
			subject_name=request.POST.get('subject')
			teachers=Teacher.objects.for_tenant(request.user.tenant).filter(staff_type="Teacher").all()
			response_data['teachers']=teachers
		#saving the class
		elif (calltype == 'save'):
			#class_name=request.POST.get('class_name')
			#subject_name=request.POST.get('subject')
			teacher_key=request.POST.get('teacher')
			year=request.POST.get('year')
			subjectTeacher=subject_teacher()
			subjectTeacher.class_section=class_name
			subjectTeacher.subject=subject_name
			subjectTeacher.teacher=Teacher.objects.for_tenant(request.user.tenant).get(staff_type="Teacher",key=teacher_key)
			subjectTeacher.year=year
			subjectTeacher.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'eduadmin/new_subjectteacher.html', {'classsection':class_section_option,})

@login_required
#This is used to add students to class. Complex frontend. Not yet done.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def class_student_add(request):
	this_tenant=request.user.tenant
	class_sections=class_section.objects.for_tenant(this_tenant)
	batch=Batch.objects.for_tenant(this_tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		students_excluded = []
		if (calltype == 'student'):
			response_data=get_student_list(request,batch,class_sections)
		if (calltype == 'save'):
			with transaction.atomic():
				# try:
				class_selectedid=request.POST.get('class_selected')
				class_selected=class_sections.get(id=class_selectedid)
				year=int(request.POST.get('year'))
				students_data = json.loads(request.POST.get('details'))
				for data in students_data:
					student_id=data['student_id']
					roll_no=data['roll_no']
					student=Student.objects.for_tenant(this_tenant).get(id=student_id)
					student_add_fee(student, class_selected, year, this_tenant)
					new_student=classstudent()
					new_student.student=student
					new_student.class_section=class_selected
					new_student.roll_no=roll_no
					new_student.year=year
					new_student.is_promoted=False
					new_student.tenant=this_tenant
					new_student.save()
				# except:
				# 	transaction.rollback()
		
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'eduadmin/class_studentadd.html', {'batch':batch,'classsection':class_sections})

@login_required
#This is the view to provide list
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def eduadmin_list(request, input_type):
	if (input_type=="Class"):
		this_tenant=request.user.tenant
		items = class_section.objects.for_tenant(this_tenant).all()
		try:			
			totalperiod=total_period.objects.get(tenant=this_tenant).number_period
			return render(request, 'eduadmin/classsection_list.html',{'items':items, 'list_for':"Classes", 'period':totalperiod})
		except:
			return render(request, 'eduadmin/classsection_list.html',{'items':items, 'list_for':"Classes"})
	elif (input_type=="Subject Teacher"):
		items = subject_teacher.objects.for_tenant(request.user.tenant).select_related('teacher').all()
		return render(request, 'eduadmin/subjectteacher_list.html',{'items':items, 'list_for':"Subjet Teachers, Year and Class Wise "})
	elif (input_type=="House"):
		items = House.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/house_list.html',{'items':items, 'list_for':"Houses"})

@login_required
#This function is used for viewing the details of a class.
# @user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def classdetail(request, detail):
	class_selected=class_section.objects.for_tenant(request.user.tenant).get(slug=detail)
	class_group=class_selected.classgroup
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		this_tenant=request.user.tenant
		if (calltype == 'year'):
			#class_name=request.POST.get('class_name')
			year=request.POST.get('year')
			response_data = []
			try:				
				#This will help us get the student list
				students_list=classstudent.objects.for_tenant(request.user.tenant).\
								filter(class_section=class_selected,year=year).select_related("student")
				for student in students_list:
					response_data.append({'data_type':'Student','key':student.student.key, 'local_id': student.student.local_id,\
						'first_name': student.student.first_name, 'last_name': student.student.last_name})
				#This will help us get the class teacher
				class_teacher=classteacher.objects.for_tenant(request.user.tenant).\
							get(class_section=class_selected,year=year)
				response_data.append({'data_type':'Teacher','key':class_teacher.class_teacher.key, \
					'first_name': class_teacher.class_teacher.first_name, 'last_name': class_teacher.class_teacher.last_name})
				#This will help us get the syllabus and the related subject teacher
				class_syllabus=Syllabus.objects.for_tenant(request.user.tenant).\
							filter(class_group=class_group,year=year).select_related("subject")
				for syllabus in class_syllabus:
					subject=syllabus.subject
					try:
						teacher=subject_teacher.objects.for_tenant(request.user.tenant).\
							filter(subject=subject, class_section=class_selected).get(year=year).select_related('teacher')
						response_data.append({'data_type':'Syllabus','subject': syllabus.subject.name,\
							'topics': syllabus.topics,'teacher':teacher.teacher.name})
					except:
						response_data.append({'data_type':'Syllabus','subject': syllabus.subject.name,'topics': syllabus.topics,})		
					
			except:
				pass
		jsondata=json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'eduadmin/class_details.html', {'class_selected':class_selected})


@login_required
#This function is used for viewing period. Adding period has to be done shortly.
#Student view is separeted out. From student view, prents view will be created.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def view_add_period(request, detail):
	extension="base.html"
	this_tenant=request.user.tenant
	class_selected=class_section.objects.for_tenant(this_tenant).get(slug=detail)
	class_group=class_selected.classgroup
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if (calltype == 'year'):
			year=request.POST.get('year')
			try:
				try:
					#This will help us get the class teacher
					class_teacher=classteacher.objects.for_tenant(request.user.tenant).\
							get(class_section=class_selected,year=year)
					response_data.append({'data_type':'Teacher','key':class_teacher.class_teacher.key, \
							'first_name': class_teacher.class_teacher.first_name, 'last_name': class_teacher.class_teacher.last_name})
				except:
					response_data.append({'data_type':'Error','message': 'Class Teacher not added to class'})
				#This will help us get the syllabus
				class_syllabus=Syllabus.objects.for_tenant(request.user.tenant).\
							filter(class_group=class_group,year=year).select_related("subject")
				for syllabus in class_syllabus:
					subject=syllabus.subject
					response_data.append({'data_type':'Syllabus','subject': subject.name,\
							'topics': syllabus.topics, 'id': subject.id})
				try:
					periods=period.objects.filter(year=year,class_section=class_selected).select_related('subject', 'teacher')
					for item in periods:
						response_data.append({'data_type':'Period','day': item.day,'period': item.period,\
							'subject': item.subject.name, 'teacher':item.teacher.first_name+" "+item.teacher.last_name})					
				except:
					pass
			except:
				pass
		elif (calltype == 'save'):
			response_data=period_add(request, class_selected)
		jsondata=json.dumps(response_data)
		return HttpResponse(jsondata)
	try:			
		totalperiod=total_period.objects.get(tenant=this_tenant).number_period
		return render (request, 'eduadmin/class_period.html', {'class_selected':class_selected, 'totalperiod': totalperiod,\
			'range':range(totalperiod), 'extension':extension})
	except:
		return render (request, 'eduadmin/class_period.html', {'class_selected':class_selected, 'extension':extension})
	
@login_required
#View a teacher's period. This is step 1 in absent teacher subsitution
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def view_teacher_period(request):
	extension="base.html"
	this_tenant=request.user.tenant
	teachers=Teacher.objects.for_tenant(this_tenant).filter(staff_type="Teacher").all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if (calltype == 'year'):
			year=request.POST.get('year')
			teacherid=request.POST.get('teacherid')
			teacher=teachers.get(id=teacherid)
			try:
				periods=period.objects.filter(year=year,teacher=teacher).select_related('subject', 'class_section')
				for item in periods:
					response_data.append({'data_type':'Period','day': item.day,'period': item.period,\
							'subject': item.subject.name, 'class_section':item.class_section.name})					
			except:
				pass
		jsondata=json.dumps(response_data)
		return HttpResponse(jsondata)
	try:			
		totalperiod=total_period.objects.get(tenant=this_tenant).number_period
		return render (request, 'eduadmin/teacher_period.html', {'totalperiod': totalperiod, 'range':range(totalperiod),\
			'extension':extension, 'teachers':teachers})
	except:
		return render (request, 'eduadmin/teacher_period.html', { 'extension':extension, 'teachers':teachers})

@login_required
#View to promote students
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def promote_student(request):
	extension="base.html"
	this_tenant=request.user.tenant
	class_section_options=class_section.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data=[]
		if (calltype == 'students'):
			from_classid=request.POST.get('from_classid')
			from_year=int(request.POST.get('from_year'))
			class_selected=class_section_options.get(id=from_classid)
			students=classstudent.objects.filter(class_section=class_selected, year=from_year, is_promoted=False)
			response_data=list(Student.objects.filter(classstudent_eduadmin_student_student__in=students).values('id','first_name',\
					'last_name','key','local_id'))
			#jsonify django querysets
		elif (calltype == 'promote'):
			from_class=request.POST.get('from_classid')
			to_class=request.POST.get('to_classid')
			from_year=int(request.POST.get('from_year'))
			to_year=int(request.POST.get('to_year'))
			from_class_selected=class_section_options.get(id=from_class)
			to_class_selected=class_section_options.get(id=to_class)
			#Getting set of student ids for validation
			list_student=classstudent.objects.for_tenant(request.user.tenant).\
					filter(class_section=from_class_selected,year=from_year)
			students_final=list(Student.objects.filter(classstudent_eduadmin_student_student__in=list_student).values('id'))
			students_set=set()
			for i in students_final:
				students_set.add(i['id'])
			students_data=json.loads(request.POST.get('details'))
			with transaction.atomic():
				try:
					for data in students_data:
						student_id=data['student_id']
						roll_no=data['roll_no']
						is_promoted=data['is_promoted']
						print(is_promoted)
						#Doing a validation, if student is actually in class
						if (is_promoted):
							if (student_id in students_set):
								student=Student.objects.for_tenant(this_tenant).get(id=student_id)
								class_student=list_student.get(student=student)
								class_student.is_promoted=True
								class_student.save()
								student_add_fee(student, to_class_selected, to_year, this_tenant)
								new_classstudent=classstudent()
								new_classstudent.class_section=to_class_selected
								new_classstudent.student=student
								new_classstudent.roll_no=roll_no
								new_classstudent.year=to_year
								new_classstudent.is_promoted=False
								new_classstudent.tenant=this_tenant
								new_classstudent.save()
							else:
								raise IntegrityError
				except:
					transaction.rollback()
		jsondata=json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'eduadmin/class_promote_student.html', { 'extension':extension, 'class_section':class_section_options})

@login_required
#This is used to create new exams. CCE is automatically created
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def exam_type_new(request):
	current_tenant=request.user.tenant
	form=ExamTypeForm(tenant=current_tenant)
	input_type="Exam Type For Current Academic Year"
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		form = ExamTypeForm(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			item.opted=True
			exam_type=form.cleaned_data['exam_type']
			year=academic_year.objects.for_tenant(current_tenant).get(current_academic_year=True).year
			item.year=year
			with transaction.atomic():
				try:
					if (exam_type == "CCE"):
						create_term("Term 1", year, current_tenant)
						create_term("Term 2", year, current_tenant)
						create_exam("Formative Assessments 1", "FA1", 1, year, current_tenant, 0.1,"Term 1")
						create_exam("Formative Assessments 2", "FA2", 2, year, current_tenant, 0.1,"Term 1")
						create_exam("Summative Assessments 1", "SA1", 3, year, current_tenant, 0.3,"Term 1")
						create_exam("Formative Assessments 3", "FA3", 4, year, current_tenant, 0.1,"Term 2")
						create_exam("Formative Assessments 4", "FA4", 5, year, current_tenant, 0.1,"Term 2")						
						create_exam("Summative Assessments 2", "SA2", 6, year, current_tenant, 0.3,"Term 2")
						create_grade_table('S',1, 100, 91,"A1", 10, current_tenant)
						create_grade_table('S',2, 90, 81,"A2", 9, current_tenant)
						create_grade_table('S',3, 80, 71,"B1", 8, current_tenant)
						create_grade_table('S',4, 70, 61,"B2", 7, current_tenant)
						create_grade_table('S',5, 60, 51,"C1", 6, current_tenant)
						create_grade_table('S',6, 50, 41,"C2", 5, current_tenant)
						create_grade_table('S',7, 40, 33,"D", 4, current_tenant)
						create_grade_table('S',8, 32, 21,"E1", 0, current_tenant)
						create_grade_table('S',9, 20, 0,"E2", 0, current_tenant)
						create_grade_table('C',1, 100, 81,"A+", 5, current_tenant)
						create_grade_table('C',2, 80, 61,"A", 4, current_tenant)
						create_grade_table('C',3, 60, 41,"B+", 3, current_tenant)
						create_grade_table('C',4, 40, 21,"B", 2, current_tenant)
						create_grade_table('C',5, 20, 0,"C", 1, current_tenant)
						item.save()
					elif (exam_type == "MG"):
						create_grade_table('S',1, 100, 100,"A+", 10, current_tenant)
						create_grade_table('S',2, 99, 90,"A", 9, current_tenant)
						create_grade_table('S',3, 89, 80,"B", 8, current_tenant)
						create_grade_table('S',4, 79, 70,"C", 7, current_tenant)
						create_grade_table('S',5, 69, 60,"D", 6, current_tenant)
						create_grade_table('S',6, 59, 40,"E", 5, current_tenant)
						create_grade_table('S',7, 39, 0,"F", 4, current_tenant)
				except:
					transaction.rollback()

			return redirect('landing')
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
#This is the base page.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def new_grade_table(request):
	this_tenant=request.user.tenant
	try:
		exam_type=exam_creation.objects.get(tenant=this_tenant).exam_type
		# if (exam_type == 'CCE'):
		# send user to view grade table
		try:
			data=grade_table.objects.for_tenant(tenant=this_tenant)
			return redirect ('eduadmin:view_grade_table')
		# send user to view grade table
		# else:
		except:
			if (request.method == 'POST'):
				grade_details = json.loads(request.POST.get('details'))
				response_data=[]
				with transaction.atomic():
					try:
						for grade in grade_details:
							create_grade_table('S', grade['sl_no'], grade['max'], grade['min'], \
								grade['grade'], grade['grade_point'], this_tenant)							
					except:
						transaction.rollback()
				jsondata=json.dumps(response_data)
				return HttpResponse(jsondata)
			return render (request, 'eduadmin/new_grade_table.html')
	except:
		return redirect ('eduadmin:new_exam_type')

@login_required
def view_grade_table(request):
	this_tenant=request.user.tenant
	grades=grade_table.objects.for_tenant(tenant=this_tenant)
	return render (request, 'eduadmin/view_grade_table.html', {'grades':grades,})

@login_required
#This has to be principal and owner only view
def period_free_teachers(request):
	this_tenant=request.user.tenant
	totalperiod=total_period.objects.get(tenant=this_tenant).number_period
	if (request.method == 'POST'):
		period_selected = request.POST.get('period')
		day_selected = request.POST.get('day')
		year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
		period_teachers=period.objects.for_tenant(this_tenant).filter(year=year, day=day_selected, period=period_selected).\
					select_related('teacher')
		excluded_teachers=Teacher.objects.filter(period_eduadmin_teacher_teacher__in=period_teachers).all()
		free_teachers=list(Teacher.objects.for_tenant(this_tenant).filter(staff_type="Teacher").exclude(teacher__in=excluded_teachers).\
					values('id','local_id','first_name','last_name'))
		return HttpResponse(json.dumps(free_teachers))
	return render (request, 'eduadmin/view_grade_table.html', {'periods':totalperiod})

@login_required
def view_exam_list(request):
	this_tenant=request.user.tenant
	extension="base.html"
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	terms=Term.objects.for_tenant(this_tenant).filter(is_active=True, year=year)
	exams=Exam.objects.for_tenant(this_tenant).filter(is_active=True, year=year)
	return render (request, 'eduadmin/view_exam_list.html', {'terms':terms, 'exams':exams, 'extension':extension})

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def publish_exam(request):
	this_tenant=request.user.tenant
	extension="base.html"
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	exams=Exam.objects.for_tenant(this_tenant).filter(is_active=True, year=year, is_published=False)
	return render (request, 'eduadmin/publish_exam.html', {'exams':exams, 'extension':extension})