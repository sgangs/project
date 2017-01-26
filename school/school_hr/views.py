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
			studentid=request.POST.get('profileid')
			email=teachers.get(id=studentid).email_id
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
    