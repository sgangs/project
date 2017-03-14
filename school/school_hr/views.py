from datetime import date, datetime, timedelta
import json
from dateutil.rrule import *
from dateutil.parser import *
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from school.user_util import user_passes_test_custom
from app_control.view_control import allow_owner_principal, allow_staff
from school_user.models import User, Tenant
from school_student.models import Student
from school_teacher.models import Teacher 
from school_genadmin.models import annual_calender, academic_year
from school_genadmin.genadmin_util import holiday_calculator
from .models import *
from .hr_utils import *
from . forms import leaveTypeForm, staffCadreForm

@login_required
#This is the base page.
def base(request):
	return render (request, 'hr/hr_base.html')

@login_required
#This is the base page.
def holiday(request):
	if (request.user.user_type=='Teacher'):
		extension="base_teacher.html"
		return render (request, 'hr/holiday.html',{'extension':extension,})
	else:
		extension="base.html"
		return render (request, 'hr/holiday.html',{'extension':extension,})

@login_required
#This is the base page.
def marked_already(request):
	if (request.user.user_type=='Teacher'):
		extension="base_teacher.html"
		return render (request, 'hr/attendance_done.html',{'extension':extension,})
	else:
		extension="base.html"
		return render (request, 'hr/attendance_done.html',{'extension':extension,})

@login_required
#This view is for registering hr models
def add_data(request, input_type):
	if (input_type == "Leave Type"):
		importform = leaveTypeForm
		name='hr:link_leave_type'
	elif (input_type == "Staff Cadre"):
		importform = staffCadreForm
		name='hr:link_cadre_teacher'
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
# Create new student profile.
#Visible only by admin/Principal/Owner - Admin has the power to create student module.
def registerStudent(request):
	students=Student.objects.for_tenant(request.user.tenant).filter(user=None, isactive=True).order_by('key')[:500]
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
# #This is used to add teacher attendance.
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

@login_required
#This view is for giving attendance. Can only be generated by staffs 
@user_passes_test_custom(allow_staff, redirect_namespace='permission_denied')
def individual_attendance(request):
	this_tenant=request.user.tenant
	today=date.today()
	# today=date.today()
	staff=Teacher.objects.get(user=request.user)
	try:
		attendance_given=teacher_attendance.objects.get(date=today,teacher=staff)
		return redirect("hr:marked_already")
	except:
		pass
	current_year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	start=current_year.start
	end=current_year.end
	if request.method == 'POST':
		staff=Teacher.objects.get(user=request.user)
		response_data = []
		is_present=request.POST.get('ispresent')
		if (is_present == 'true'):
			is_present=True
		else:
			is_present=False
		current_leave_type=request.POST.get('leavetype')
		remarks=request.POST.get('remarks')
		new_attendance=teacher_attendance()
		new_attendance.ispresent=is_present
		new_attendance.is_authorized=False
		new_attendance.teacher=staff
		if not is_present:
			new_attendance.leave_type=leave_type.objects.for_tenant(this_tenant).get(id=current_leave_type)
			new_attendance.remarks=remarks
		new_attendance.date=today
		new_attendance.tenant=this_tenant
		new_attendance.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	try:
		events= annual_calender.objects.for_tenant(request.user.tenant).filter(date__range=(today,today)).all()
		events_hol=events.filter(attendance_type=2)
		if events_hol:
			return redirect('hr:holiday')
	except:
		events=[]
	hol=[]
	hol=holiday_calculator(today, today, events, hol)
	if hol:
		return redirect('hr:holiday')
	try:
		staff=Teacher.objects.get(user=request.user)
		attendance_given=teacher_attendance.get(date=today,teacher=staff)
		if attendance_given:
			return HttpResponse('Your attendance is already registered')
	except:
		pass
	current_staff_cadre=staff_cadre_linking.objects.for_tenant(this_tenant).get(teacher=staff, year=current_year.year)
	cadre=staff_cadre.objects.get(staffCadreLinking_staffCadre=current_staff_cadre)
	leave_list=cadre_leave.objects.for_tenant(this_tenant).filter(cadre=cadre, year=current_year.year)
	leaves=[]
	for item in leave_list:
		leave=leave_type.objects.for_tenant(this_tenant).get(cadreLeave_leaveType=item)
		leaves_applied=teacher_attendance.objects.filter(teacher=staff, date__range=(start,end), leave_type=leave).count()
		leaves_available=item.numbers-leaves_applied
		leaves.append({'id':leave.id,'name':leave.name, 'applied':leaves_applied,'available':leaves_available})
	return render(request, 'hr/individual_attendance.html',{'leaves':leaves,})
	
@login_required
#This view is for giving attendance. Can only be generated by staffs 
@user_passes_test_custom(allow_staff, redirect_namespace='permission_denied')
def apply_leave(request):
	this_tenant=request.user.tenant
	staff=Teacher.objects.get(user=request.user)
	if (request.user.user_type=='Teacher'):
		extension="base_teacher.html"		
	else:
		extension="base.html"
	current_year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	start=current_year.start
	end=current_year.end
	if request.method == 'POST':
		response_data = []
		date=datetime.strptime((request.POST.get('date')), '%Y-%m-%d')
		current_leave_type=request.POST.get('leavetype')
		entry_type=request.POST.get('entry_type') #Get the entry type: leave or mispunch
		remarks=request.POST.get('remarks')
		try:
			events= annual_calender.objects.for_tenant(request.user.tenant).filter(date__range=(date,date)).all()
			events_hol=events.filter(attendance_type=2)
			if events_hol:
				return HttpResponse(json.dumps("Holiday"))
		except:
			events=[]
		hol=[]
		hol=holiday_calculator(date, date, events, hol)
		if hol:
			return HttpResponse(json.dumps("Holiday"))
		try:
			attendance_given=teacher_attendance.objects.get(date=date,teacher=staff)
		except:
			attendance_given=''
		if attendance_given:
			new_attendance=attendance_given
		else:
			new_attendance=teacher_attendance()
		if (entry_type == "Mispunch"):
			new_attendance.ispresent=True
			new_attendance.attendance_type=2
		else:
			new_attendance.ispresent=False
			new_attendance.leave_type=leave_type.objects.for_tenant(this_tenant).get(id=current_leave_type)
		new_attendance.is_authorized=False
		new_attendance.teacher=staff		
		new_attendance.date=date
		new_attendance.tenant=this_tenant
		new_attendance.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	current_staff_cadre=staff_cadre_linking.objects.for_tenant(this_tenant).get(teacher=staff, year=current_year.year)
	cadre=staff_cadre.objects.get(staffCadreLinking_staffCadre=current_staff_cadre)
	leave_list=cadre_leave.objects.for_tenant(this_tenant).filter(cadre=cadre, year=current_year.year)
	leaves=[]
	for item in leave_list:
		leave=leave_type.objects.for_tenant(this_tenant).get(cadreLeave_leaveType=item)
		leaves_applied=teacher_attendance.objects.filter(teacher=staff, date__range=(start,end), leave_type=leave).count()
		leaves_available=item.numbers-leaves_applied
		leaves.append({'id':leave.id,'name':leave.name, 'applied':leaves_applied,'available':leaves_available})
	return render(request, 'hr/apply_leave.html',{'leaves':leaves, "extension":extension})


@login_required
#This view is for authorizing attendance. Permission for principal/owner
@user_passes_test_custom(allow_owner_principal, redirect_namespace='permission_denied')
def attendance_approval(request):
	this_tenant=request.user.tenant
	#Filter attendances for all but principal. Principal attendance to be authorized by owner.
	attendances_original=teacher_attendance.objects.for_tenant(this_tenant).filter(is_authorized=False).\
						order_by('date').select_related('teacher', 'leave_type')
	if request.method == 'POST':
		response_data=[]
		attendances=json.loads(request.POST.get('attendances'))
		with transaction.atomic():
			try:
				for data in attendances:
					attendance_id=request.POST.get('id')
					is_authorized=request.POST.get('authorize')
					is_rejected=request.POST.get('reject')
					if (is_authorized):
						attendance=attendances_original.get(id=attendance_id)
						attendance.is_authorized=True
						attendance.save()
					elif (is_rejected):
						attendances_original.get(id=attendance_id).delete()
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render(request, 'hr/staff_attendance_approval.html',{'attendances': attendances_original})

