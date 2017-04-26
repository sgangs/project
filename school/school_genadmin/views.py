from datetime import date, datetime
from dateutil.rrule import *
from dateutil.parser import *
from django.utils import timezone
from django.utils.timezone import localtime
from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F

from school.user_util import user_passes_test_custom
from school_user.models import Tenant
from school_account.models import accounting_period
from .forms import *
from .models import *
from .genadmin_util import *
from .genadmin_view_control import *
from app_control.view_control import *


@login_required
#This is the base page.
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def base(request):
	return render (request, 'genadmin/genadmin_base.html')

@login_required
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
#For adding new entry for Genadmin models
def genadmin_new(request, input_type):
	extension="base.html"
	if (input_type == "Subject"):
		importform = SubjectForm
		name='genadmin:subject_list'
	elif (input_type == "Class Group"):
		importform = classGroupForm
		name='genadmin:class_group_list'
	elif (input_type == "House"):
		importform = HouseForm
		name='genadmin:house_list'
	elif (input_type == "Academic Year"):
		importform = academicYearForm
		name='landing'
	elif (input_type == "Batch"):
		importform = BatchForm
		name='landing'
		input_type="Student Batch"
	elif (input_type == "Notice"):
		importform = NoticeForm
		name='landing'
	
	# elif (input_type == "Pass"):
	# 	importform = GatePassForm
	# 	name='genad,in:gate_pass_list'
	# 	input_type="Gate Pass"
	
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			with transaction.atomic():
				try:
					if (input_type == "academic_year"):
						data=form.cleaned_data
						current=data['current_academic_year']
						try:
							if current:
								ay=academic_year.objects.for_tenant(current_tenant).get(current_academic_year=True)
								ay.current_academic_year=False
								ay.save()
						except:
							pass
					item=form.save(commit=False)			
					item.tenant=current_tenant
					item.save()
					return redirect(name)
				except:
					transaction.rollback()			
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})

@login_required
#This is the view to provide list
@user_passes_test_custom(allow_admincontrol, redirect_namespace='permission_denied')
def master_list(request, input_type):
	extension="base.html"
	#for the delete button to work - Do we need to have the delete option? 
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
	if (input_type=="Subject"):
		items = Subject.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/subject_list.html',{'items':items, 'list_for':"Subjects", 'extension':extension})
	elif (input_type=="Class Group"):
		items = class_group.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/classgroup_list.html',{'items':items, 'list_for':"Class Groups", 'extension':extension})
	elif (input_type=="House"):
		items = House.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/house_list.html',{'items':items, 'list_for':"Houses", 'extension':extension})
	elif (input_type=="Batch"):
		items = Batch.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/house_list.html',{'items':items, 'list_for':"Batch", 'extension':extension})


@login_required
#This is a event list view - Change period to academic year period
def academic_year_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	years=academic_year.objects.for_tenant(this_tenant).all().order_by('start','end')
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}
		if (calltype == 'newacadyear'):
			year=int(request.POST.get('year'))
			start=request.POST.get('start')
			end=request.POST.get('end')
			current=request.POST.get('current')
			if (current=='true'):
				current=True
			else:
				current=False
			# exist_start=years.get(start=start)
			# response_data['start']="Start Exists"
			# proceed=False
			with transaction.atomic():
				try:
					proceed=True
					try:
						exist_year=years.get(year=year)
						response_data['year']="Year Exists"
						proceed=False
					except:
						pass
					try:
						exist_start=years.get(start=start)
						response_data['start']="Start Exists"
						proceed=False
					except:
						pass
					try:
						exist_end=years.get(end=end)
						response_data['end']="End Exists"
						proceed=False
					except:
						pass
					if (start>end):
						response_data['start-end']="Start gt End"
						proceed=False
					if (proceed):
						new_year=academic_year()
						new_year.year=year
						new_year.start=start
						new_year.end=end
						new_year.current_academic_year=current
						new_year.tenant=this_tenant
						if (current):
							current_year=years.get(current_academic_year=True)
							current_year.current_academic_year=False
							current_year.save()
						new_year.save()
				except:
					pass
		if (calltype == 'changeacadyear'):
			yearid = request.POST.get('new_acad_year')
			with transaction.atomic():
				try:
					current_year=years.get(current_academic_year=True)
					current_year.current_academic_year=False
					current_year.save()
					new_year=years.get(id=yearid)
					new_year.current_academic_year=True
					new_year.save()
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/academic_year.html',{'items':years , 'extension':extension})


@login_required
def subject_data(request):
	extension="base.html"
	this_tenant=request.user.tenant
	subjects=Subject.objects.for_tenant(this_tenant).all().order_by('name')
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = {}		
		name=request.POST.get('name')
		proceed=True
		try:
			is_subject=subjects.get(name=name)
			proceed=False
			response_data['name']='Name exists'
		except:
			pass
		print(proceed)
		if (proceed):
			new_subject=Subject()
			new_subject.name=name
			new_subject.tenant=this_tenant
			new_subject.save()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/subject.html',{'items':subjects , 'extension':extension})


@login_required
#This is a calander and event add view.
def calendar(request):
	extension="base.html"
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if (calltype == 'eventsave'):
			eventname=request.POST.get('eventname')
			date=request.POST.get('date')
			eventtype=int(request.POST.get('eventtype'))
			attendance_type=int(request.POST.get('atttype'))
			calendar_event=annual_calender()
			calendar_event.event=eventname
			date_formatted=datetime.strptime(date, "%Y-%m-%d").date()
			datetime_final=datetime.combine(date_formatted, datetime.min.time())
			calendar_event.date=timezone.make_aware(datetime_final, timezone.get_current_timezone())
			calendar_event.tenant=request.user.tenant
			calendar_event.event_type=eventtype
			if (eventtype == 1):
				calendar_event.attendance_type=2
			elif (eventtype == 3):
				calendar_event.attendance_type=1
			else:
				calendar_event.attendance_type=attendance_type			
			calendar_event.save()			
		elif (calltype == 'rulesave'):
			title=request.POST.get('title')
			week=json.loads(request.POST.get('week'))
			day=int(request.POST.get('day'))
			week.sort()
			# print(type(week[0]))
			week=map(str,week)
			week=''.join(week)
			rule=annual_holiday_rules()
			rule.title=title
			rule.day=day			
			rule.week=int(week)
			rule.tenant=request.user.tenant
			rule.save()
		elif (calltype == 'event'):
			start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d").date()
			end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d").date()
			#Appends all events
			events= annual_calender.objects.for_tenant(request.user.tenant).filter(date__range=(start,end))
			for event in events:
				response_data.append({'event_type':event.event_type,'title':event.event, 'start': localtime(event.date).isoformat(),\
									'id':event.id,'allDay':True})
			rules=annual_holiday_rules.objects.for_tenant(request.user.tenant)
			hol=[] #To store all holidays here.
			hol=holiday_calculator(start, end, events, hol)
			#Appends working holidays
			for i in hol:
				response_data.append({'event_type':"Weekly",'title':"Weekly Holiday", 'start': i.isoformat(), 'allDay':True})
		if (calltype == 'delete'):
			event_id=request.POST.get('event_id')
			annual_calender.objects.for_tenant(request.user.tenant).get(id=event_id).delete()

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/calendar.html', {'extension':extension})

@login_required
#This is a event list view - Change period to academic year period
def calendar_list(request):
	extension="base.html"
	this_tenant=request.user.tenant
	period=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True)
	events=annual_calender.objects.for_tenant(request.user.tenant).filter(date__range=(period.start,period.end)).order_by('date')
	return render (request, 'genadmin/event_list.html',{'items':events, 'list_for':'Events' , 'extension':extension})

#Nothing Done
@login_required
def view_gate_passes(request):
	this_tenant=request.user.tenant
	if request.method == 'POST':
		start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d").date()
		end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d").date()
		passes= gate_pass.objects.for_tenant(request.user.tenant).filter(date__range=(start,end))
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/event_list.html')

#Frontend pending
@login_required
def notice_event_delete(request, calltype):
	this_tenant=request.user.tenant
	extension='base.html'
	if request.method == 'POST':
		response_data=[]
		details = json.loads(request.POST.get('details'))
		if (calltype == 'Notice'):
			for item in details:
				notice_board.objects.for_tenant(request.user.tenant).get(id__exact=item['item_id']).delete()
		elif (calltype == 'Event'):
			for item in details:
				annual_calender.objects.for_tenant(request.user.tenant).get(id__exact=item['item_id']).delete()			
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	if (calltype == 'Notice'):
		items=notice_board.objects.for_tenant(this_tenant).order_by('show_from')
	elif (calltype == 'Event'):
		items=annual_calender.objects.for_tenant(this_tenant).order_by('date')
	return render (request, 'genadmin/delete_event_notice.html', {'items':items,'calltype':calltype, 'extension':extension})


#Frontend pending
@login_required
def change_class_name(request):
	extension='base.html'
	this_tenant=request.user.tenant
	classgroups=class_group.objects.for_tenant(this_tenant)
	if request.method == 'POST':
		response_data=[]
		classid = request.POST.get('classid')
		new_name=request.POST.get('new_name')
		class_group_selected=class_group.objects.for_tenant(this_tenant).get(id=classid)
		class_group_selected.name=new_name
		class_group_selected.save()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)	
	class_groups=class_group.objects.for_tenant(this_tenant).all()
	return render (request, 'genadmin/change_class_name.html', {'classgroups':classgroups, 'extension':extension})

#Frontend yet to be designed
@login_required
#This should be an owner only view
def change_academic_year(request):
	this_tenant=request.user.tenant
	extension='base.html'
	years_list=academic_year.objects.for_tenant(this_tenant).all()
	if request.method == 'POST':
		response_data=[]
		yearid = request.POST.get('new_acad_year')
		with transaction.atomic():
			try:
				current_year=years_list.get(current_academic_year=True)
				current_year.current_academic_year=False
				current_year.save()
				new_year=years_list.get(id=yearid)
				new_year.current_academic_year=True
				new_year.save()				
			except:
				transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/change_academic_year.html', {'years':years_list, 'extension':extension})