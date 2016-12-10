from functools import partial, wraps
import json
#from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F

from .forms import SyllabusForm, ExamForm, ClassTeacherForm, ExaminerForm
from .models import class_section, classteacher, classstudent, Syllabus, Exam, Examiner, subject_teacher
from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import class_group, Subject

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
				objecgt_sucess = class_section.objects.for_tenant(this_tenant).get(name__exact=classname)
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
		name='genadmin:unit_list'
	elif (input_type=="Exam"):
		importform=ExamForm
		name='genadmin:unit_list'
	elif (input_type=="ClassTeacher"):
		importform=ClassTeacherForm
		name='genadmin:unit_list'
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
			item.save()
			return redirect(name)
	#else:
	#	form=importform(tenant=request.user.tenant)	
	#return render(request, 'master/new.html',{'formset': formset, 'helper': helper, 'item': type})
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
#This viw is used for entering exam invigilators
def examiner_new(request):
	name='genadmin:unit_list'
	current_tenant=request.user.tenant
	form=ExaminerForm(tenant=current_tenant)
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		form = ExaminerForm(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)
			item.tenant=current_tenant
			unique_class=cd.get('class_section')
			unique_exam=cd.get('exam')
			unique_subject=cd.get('subject')
			year=Exam.objects.for_tenant(request.user.tenant).get_object_or_404(name=unique_exam).year
			item.internal_examiner=subject_teacher.filter(class_section=unique_class).filter(subject=unique_subject).\
									filter(year=year).teacher
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': "Examiner"})

@login_required
# #This is used to add subject teachers. Select option is based on previous selection
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

	return render (request, 'eduadmin/new_subjectteacher.html', {'classsection':classsection,})