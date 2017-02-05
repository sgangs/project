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

from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import class_group, Subject
from school_fees.models import student_fee, group_default_fee
from .forms import SyllabusForm, ExamForm, ClassTeacherForm, ExaminerForm, ClassStudentForm, SubjectTeacherForm, TotalPeriodForm
from .models import class_section, classteacher, classstudent, Syllabus, Exam, Examiner, subject_teacher, total_period
from .eduadmin_util import *


@login_required
#This is the base page.
def base(request):
	return render (request, 'eduadmin/eduadmin_base.html')


@login_required
#This function helps in creating new class
def class_new(request):
	#date=datetime.now()
	group=class_group.objects.for_tenant(request.user.tenant)
	class_teacher=Teacher.objects.for_tenant(request.user.tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
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
						teacher.class_teacher=Teacher.objects.for_tenant(request.user.tenant).get(key__exact=teacher_key)

						teacher.year=year
						teacher.tenant=this_tenant
						teacher.save()
				# except IntegrityError:
				# 	transaction.rollback()
				# 	response_data['name']='Name exists'
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'eduadmin/new_class.html', {'groups':group,'teachers': class_teacher})
	
@login_required
#This function helps in addidng new syllabus and exams
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
	elif (input_type=="Subject Teacher"):
		importform=SubjectTeacherForm
		name='eduadmin:subject_teacher_list'
	elif (input_type=="Examiner"):
		importform=ExaminerForm
		name='eduadmin:examiner_list'
	elif (input_type=="Total Period"):
		importform=TotalPeriodForm
		name='eduadmin:class_list'
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
					# try:
					item.save()
						# try:
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
					# 	except:
					# 		pass
					# except:
					# 	transaction.rollback()
			else:
				item.save()
			return redirect(name)
	#else:
	#	form=importform(tenant=request.user.tenant)	
	#return render(request, 'master/new.html',{'formset': formset, 'helper': helper, 'item': type})
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

# @login_required
# #This view is used for entering exam invigilators. Nothing is done yet.
# def examiner_new(request):
# 	name='genadmin:unit_list'
# 	current_tenant=request.user.tenant
# 	form=ExaminerForm(tenant=current_tenant)
# 	if (request.method == "POST"):
# 		current_tenant=request.user.tenant
# 		form = ExaminerForm(request.POST, tenant=current_tenant)
# 		if form.is_valid():
# 			item=form.save(commit=False)
# 			item.tenant=current_tenant
# 			unique_class=cd.get('class_section')
# 			unique_exam=cd.get('exam')
# 			unique_subject=cd.get('subject')
# 			year=Exam.objects.for_tenant(request.user.tenant).get_object_or_404(name=unique_exam).year
# 			item.internal_examiner=subject_teacher.filter(class_section=unique_class).filter(subject=unique_subject).\
# 									filter(year=year).teacher
# 			item.save()
# 			return redirect(name)
# 	return render(request, 'genadmin/new.html',{'form': form, 'item': "Examiner"})

@login_required
#This is used to add subject teachers. Nothing is done yet.
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
			teachers=Teacher.objects.for_tenant(request.user.tenant).filter(subject=subject_name)
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
			subjectTeacher.teacher=Teacher.objects.for_tenant(request.user.tenant).filter(key=teacher_key)
			subjectTeacher.year=year
			subjectTeacher.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'eduadmin/new_subjectteacher.html', {'classsection':class_section_option,})

@login_required
#This is used to add students to class. Complex frontend. Not yet done.
def class_student_add(request):
	class_section_option=class_section.objects.for_tenant(request.user.tenant)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		students_excluded = []
		this_tenant=request.user.tenant
		if (calltype == 'year'):
			#class_name=request.POST.get('class_name')
			year=request.POST.get('year')
			students_excluded_list=classstudent.objects.for_tenant(request.user.tenant).filter(year=year)
			for item in students_excluded_list:
				students_excluded.append(item.student.id)

			students=Student.objects.for_tenant(request.user.tenant).exclude(id__in=students_excluded)
			jsondata = serializers.serialize('json', students)
		return HttpResponse(jsondata)

		#saving the class
		if (calltype == 'save'):
			try:
				class_name=request.POST.get('class_name')
				#subject_name=request.POST.get('subject')
				#teacher_key=request.POST.get('teacher')
				for data in bill_data:
					itemcode=data['itemCode']
					subitemcode=data['subitemCode']
					unit_entry=data['unit']
					unit=Unit.objects.for_tenant(this_tenant).get(symbol__iexact=unit_entry)
					item=Product.objects.for_tenant(request.user.tenant).get(key__iexact=itemcode)
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'eduadmin/class_studentadd.html', {'classsections':class_section_option,})

@login_required
#This is the view to provide list
def eduadmin_list(request, input_type):
	#for the delete button to work
	# if request.method == 'POST':
	# 	itemtype = request.POST.get('type')
	# 	itemkey = request.POST.get('itemkey')
	# 	response_data = {}
	# 	if (itemtype == 'Period'):
	# 		item = Period.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
	# 		response_data['name'] = itemkey
	# 		jsondata = json.dumps(response_data)
	# 		return HttpResponse(jsondata)
	# 	elif (itemtype == 'Chart'):
	# 		item = accountChart.objects.for_tenant(request.user.tenant).get(key__iexact=itemkey).delete()
	# 		response_data['name'] = itemkey
	# 		jsondata = json.dumps(response_data)
	# 		return HttpResponse(jsondata)	
	
	#for the list to be displayed	
	if (input_type=="Class"):
		this_tenant=request.user.tenant
		items = class_section.objects.for_tenant(this_tenant).all()
		try:			
			totalperiod=total_period.objects.get(tenant=this_tenant).number_period
			return render(request, 'eduadmin/classsection_list.html',{'items':items, 'list_for':"Classes", 'period':totalperiod})
		except:
			return render(request, 'eduadmin/classsection_list.html',{'items':items, 'list_for':"Classes"})
	elif (input_type=="Subject Teacher"):
		items = subject_teacher.objects.for_tenant(request.user.tenant).select_related().all()
		return render(request, 'eduadmin/subjectteacher_list.html',{'items':items, 'list_for':"Subjet Teachers, Year and Class Wise "})
	elif (input_type=="House"):
		items = House.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/house_list.html',{'items':items, 'list_for':"Houses"})

@login_required
#This function is used for viewing the details of a class.
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
			#combined_json = list(chain(students_list, class_teacher))
			#jsondata = serializers.serialize('json', class_teacher)
		jsondata=json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'eduadmin/class_details.html', {'class_selected':class_selected})


@login_required
#This function is used for viewing period. Adding period has to be done shortly.
#Student view is separeted out. From student view, prents view will be created.
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
	
