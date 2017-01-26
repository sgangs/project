from datetime import date, datetime
from django.utils import timezone
from django.utils.timezone import localtime
from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F


from school_user.models import Tenant
from .forms import SubjectForm, classGroupForm, HouseForm
from .models import Subject, class_group, House, annual_calender


@login_required
#This is the base page.
def base(request):
	return render (request, 'genadmin/genadmin_base.html')

@login_required
#For adding new entry for Genadmin models
def genadmin_new(request, input_type):
	if (input_type == "Subject"):
		importform = SubjectForm
		name='genadmin:subject_list'
	elif (input_type == "class_group"):
		importform = classGroupForm
		name='genadmin:class_group_list'
	elif (input_type == "House"):
		importform = HouseForm
		name='genadmin:house_list'
	# elif (input_type == "Unit"):
	# 	importform = TotalPeriodForm
	# 	name='master:unit_list'
	
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	#importformset=formset_factory(wraps(importform)(partial(importform, tenant=current_tenant)), extra=3)
	#formset=importformset()
	#helper=ManufacturerFormSetHelper()
	if (request.method == "POST"):
		#current_tenant=request.user.tenant
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
#This is the view to provide list
def master_list(request, input_type):
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
		return render(request, 'genadmin/subject_list.html',{'items':items, 'list_for':"Subjects"})
	elif (input_type=="Class Group"):
		items = class_group.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/classgroup_list.html',{'items':items, 'list_for':"Class Groups"})
	elif (input_type=="House"):
		items = House.objects.for_tenant(request.user.tenant).all()
		return render(request, 'genadmin/house_list.html',{'items':items, 'list_for':"Houses"})

@login_required
#This is a calander and event add view.
def calender(request):
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data = []
		if (calltype == 'save'):
			eventname=request.POST.get('eventname')
			date=request.POST.get('date')
			calender_event=annual_calender()
			calender_event.event=eventname
			date_formatted=datetime.strptime(date, "%Y-%m-%d").date()
			datetime_final=datetime.combine(date_formatted, datetime.min.time())
			calender_event.date=timezone.make_aware(datetime_final, timezone.get_current_timezone())
			calender_event.tenant=request.user.tenant	
			calender_event.save()
		if (calltype == 'event'):
			events = annual_calender.objects.for_tenant(request.user.tenant).all()
			for event in events:
 				response_data.append({'title':event.event, 'start': localtime(event.date).isoformat(), 'allDay':True})
 				#print (localtime(event.date).isoformat())
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'genadmin/calendar.html')

@login_required
#This is a event list view.
def calender_list(request):
	events = annual_calender.objects.for_tenant(request.user.tenant).all()
	# if request.method == 'POST':
	# 	itemtype = request.POST.get('type')
	# 	itemkey = request.POST.get('itemkey')
	# 	response_data = {}

	# 	if (itemtype == 'Manufacturer'):
	# 		item = Manufacturer.objects.get(key__iexact=itemkey).delete()
	# 		response_data['name'] = itemkey
	# 		jsondata = json.dumps(response_data)
	# 		return HttpResponse(jsondata)
	return render (request, 'genadmin/event_list.html',{'items':events, 'list_for':'Events'})