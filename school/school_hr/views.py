from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render

from school_user.models import User, Tenant
from school_student.models import Student
from school_teacher.models import Teacher
from .models import leave_type
from . forms import leaveTypeForm

@login_required
#This is the base page.
def base(request):
	return render (request, 'hr/hr_base.html')

@login_required
# Create new student profile.
#Visible only by admin/Principal/Owner - Admin has the power to create student module.
def registerStudent(request):
	students=Student.objects.for_tenant(request.user.tenant).filter(user=None)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		#saving the class
		if (calltype == 'mail'):
			studentid=request.POST.get('profileid')
			email=students.get(id=studentid).email_id
			response_data['email'] = email

		elif (calltype == 'user'):
			user=request.POST.get('user')
			try:
				email=User.objects.get(username=user)
				response_data['error'] = "Username exist"
			except:
				response_data['error'] = "Username does not exist"
			
		elif (calltype == 'save'):
			with transaction.atomic():
				try:
					studentid=request.POST.get('profileid')
					email=request.POST.get('email')
					username=request.POST.get('user')
					password=request.POST.get('pass')
					repeat=request.POST.get('repeat')
					validate_email(email)
					if (password != repeat):
						response_data['error'] = "Password Match Error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					student=students.get(id=studentid)
					user=User()
					user.username=username
					user.user_type='Student'
					user.first_name=student.first_name
					user.last_name=student.last_name
					if (email == "" or email == None):
						response_data['error'] = "Email is None error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					else:
						user.email=email
						student.email_id=email
					user.set_password(password)
					user.tenant=this_tenant
					user.save()
					student.user=user
					student.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render(request,'hr/new_profile.html', {'items':students, 'called_for':'student'})

@login_required
#This view isfor registering teacher
def registerTeacher(request):
	teachers=Teacher.objects.for_tenant(request.user.tenant).filter(user=None)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		this_tenant=request.user.tenant
		#saving the class
		if (calltype == 'mail'):
			teacherid=request.POST.get('profileid')
			email=teachers.get(id=teacherid).email_id
			response_data['email'] = email

		elif (calltype == 'user'):
			user=request.POST.get('user')
			try:
				email=User.objects.get(username=user)
				response_data['error'] = "Username exist"
			except:
				response_data['error'] = "Username does not exist"
			
		elif (calltype == 'save'):
			with transaction.atomic():
				try:
					teacherid=request.POST.get('profileid')
					email=request.POST.get('email')
					username=request.POST.get('user')
					password=request.POST.get('pass')
					repeat=request.POST.get('repeat')
					validate_email(email)
					if (password != repeat):
						response_data['error'] = "Password Match Error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					teacher=teachers.get(id=teacherid)
					user=User()
					user.username=username
					user.user_type='Teacher'
					user.first_name=teacher.first_name
					user.last_name=teacher.last_name
					if (email == "" or email == None):
						response_data['error'] = "Email is None error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					else:
						user.email=email
						teacher.email_id=email
					user.set_password(password)
					user.tenant=this_tenant
					user.save()
					teacher.user=user
					teacher.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render(request,'hr/new_profile.html', {'items':teachers,'called_for':'teacher'})


@login_required
#This view isfor registering teacher
def add_leave(request, input_type):
	if (input_type == "Leave Type"):
		importform = leaveTypeForm
		name='hr:base'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
#This is used to add teacher attendance.
def attendance_employee(request, input_type):
	this_tenant=request.user.tenant
	if (input_type == 'Teacher'):
		teachers=Teacher.objects.for_tenant(this_tenant)
		leaves=leave_type.objects.for_tenant(this_tenant).all()
	# class_section_option=class_section.objects.for_tenant(request.user.tenant)
	# if request.method == 'POST':
	# 	calltype = request.POST.get('calltype')
	# 	response_data = {}
	# 	this_tenant=request.user.tenant
	# 	if (calltype == 'class_selection'):
	# 		class_name=request.POST.get('class_name')
	# 		classgroup=class_section.get_object_or_404(name=class_name).classgroup
	# 		subject_options=Syllabus.objects.for_tenant(request.user.tenant).filter(class_group=classgroup).subject
	# 		response_data['subjects'] = subject_options
	# 	#saving the class
	# 	elif (calltype == 'save'):
	# 		#class_name=request.POST.get('class_name')
	# 		#subject_name=request.POST.get('subject')
	# 		teacher_key=request.POST.get('teacher')
	# 		year=request.POST.get('year')
	# 		subjectTeacher=subject_teacher()
	# 		subjectTeacher.class_section=class_name
	# 		subjectTeacher.subject=subject_name
	# 		subjectTeacher.teacher=Teacher.objects.for_tenant(request.user.tenant).filter(key=teacher_key)
	# 		subjectTeacher.year=year
	# 		subjectTeacher.save()
	# 	jsondata = json.dumps(response_data)
	# 	return HttpResponse(jsondata)

	return render (request, 'hr/teacher_attendance.html', {'items':teachers,'leave_types':leaves})