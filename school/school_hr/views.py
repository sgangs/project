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
from .models import *
from .hr_utils import *
from . forms import leaveTypeForm, staffCadreForm

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
	teachers=Teacher.objects.for_tenant(request.user.tenant).filter(staff_type="Teacher",user=None)
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
#This view is for registering hr models
def add_data(request, input_type):
	if (input_type == "Leave Type"):
		importform = leaveTypeForm
		name='hr:base'
	elif (input_type == "Staff Cadre"):
		importform = staffCadreForm
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
#This view is for liking leave with cadres
def link_leave(request):
	this_tenant=request.user.tenant
	cadres_list=list(staff_cadre.objects.for_tenant(this_tenant).values('id','name'))
	leaves_list=list(leave_type.objects.for_tenant(this_tenant).values('id','name','key',))
	cadres=json.dumps(cadres_list)
	leaves=json.dumps(leaves_list)
	if request.method == 'POST':
		response_data = []
		# saving the cadre-leave link
		with transaction.atomic():
			try:
				response_data=create_leave_cadre_link(request)
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'hr/cadre_linking.html',{'cadres': cadres, 'leaves': leaves})


@login_required
#This view is for liking cadres with teachers
def link_staff_teachers(request):
	this_tenant=request.user.tenant
	cadres=list(staff_cadre.objects.for_tenant(this_tenant).filter(cadre_type='Teacher').values('id','name'))
	teachers=list(Teacher.objects.for_tenant(this_tenant).filter(staff_type='Teacher').values('id','first_name','last_name','key',))
	if request.method == 'POST':
		response_data = []
		# print(request.POST)
		# saving the cadre-leave link
		with transaction.atomic():
			try:
				response_data=create_staff_cadre_link(request)
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'hr/cadre_teacher_linking.html',{'cadres': cadres, 'teachers': teachers})


@login_required
#This is used to add teacher attendance.
def attendance_employee(request, input_type):
	this_tenant=request.user.tenant
	if (input_type == 'Teacher'):
		teachers=Teacher.objects.for_tenant(this_tenant).filter(staff_type="Teacher").all()
		leaves=leave_type.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		response_data = []
		date=request.POST.get('date')
		attendances = json.loads(request.POST.get('attendances'))
		with transaction.atomic():
			try:
				for data in attendances:
					teacherid=data['teacherid']
					ispresent=data['ispresent']
					absenttype=data['absenttype']
					remarks=data['remarks']
					if (ispresent=='' or ispresent == False):
						if (absenttype=='' or absenttype=='Dont'):
							raise IntegrityError
					else:
						if (absenttype !='' and absenttype !='Dont'):
							raise IntegrityError
					new_attendance=teacher_attendance()
					teacher=Teacher.objects.for_tenant(this_tenant).get(id=teacherid)
					new_attendance.teacher=teacher
					new_attendance.date=date
					new_attendance.ispresent=ispresent
					new_attendance.remarks=remarks
					if (absenttype):
						if (absenttype != "Dont"):
							leave=leave_type.objects.for_tenant(this_tenant).get(id=absenttype)
							new_attendance.leave_type=leave
					new_attendance.tenant=this_tenant
					new_attendance.save()
			except:
				transaction.rollback()

		
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	return render (request, 'hr/teacher_attendance.html', {'items':teachers,'leave_types':leaves})