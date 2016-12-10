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
from .models import Subject, class_group, House


@login_required
#For adding new entry for Manufacturer, Unit, Zone, Vendor & Account
def genadmin_new(request, input_type):
	if (input_type == "Subject"):
		importform = SubjectForm
		name='genadmin:unit_list'
	elif (input_type == "class_group"):
		importform = classGroupForm
		name='genadmin:unit_list'
	elif (input_type == "House"):
		importform = HouseForm
		name='genadmin:unit_list'
	# elif (input_type == "Unit"):
	# 	importform = UnitForm
	# 	name='master:unit_list'
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
#landing page
def calender(request):
	return render (request, 'genadmin/calendar.html')