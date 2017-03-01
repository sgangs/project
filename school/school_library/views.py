from datetime import date, datetime
from django.utils import timezone
from django.utils.timezone import localtime
from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
#from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F


from school_user.models import Tenant
from school_eduadmin.models import class_section, classstudent
from school_genadmin.models import class_group
from school_student.models import Student
from .forms import LibraryForm, BookForm, PeriodForm
from .models import Library, Book, issue_period


@login_required
#This is used to add nes object for library models
def library_new(request, input_type):
	if (input_type == "Library"):
		importform = LibraryForm
		name='genadmin:subject_list'
	elif (input_type == "Book"):
		importform = BookForm
		name='library:book_list'
	elif (input_type == "Period"):
		importform = PeriodForm
		name='library:book_list'
		input_type="Book Holding Period"
	# elif (input_type == "Unit"):
	# 	importform = TotalPeriodForm
	# 	name='master:unit_list'
	
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	return render(request, 'library/new.html',{'form': form, 'item': input_type})

def library_list(request, input_type):
	if (input_type == "Library"):
		libraries = Library.objects.for_tenant(request.user.tenant).all()
		return render(request, 'library/list_base.html',{'libraries': libraries})
	elif (input_type == "Book"):
		books = Book.objects.for_tenant(request.user.tenant).all().select_related('subject')
		return render(request, 'library/book_list.html',{'books': books, 'list_for':'Books'})
	# elif (input_type == "Unit"):
	# 	importform = TotalPeriodForm
	# 	name='master:unit_list'

@login_required
#This is a calander and event add view.
def book_issue(request):
	this_tenant=request.user.tenant
	books=Book.objects.for_tenant(this_tenant).filter(book_issued=False).all()
	classlist=class_section.objects.for_tenant(this_tenant).all()
	# if request.method == 'POST':
	# 	calltype=request.POST.get('calltype')
	# 	response_data = []
	# 	if (calltype == 'save'):
	# 		eventname=request.POST.get('eventname')
	# 		date=request.POST.get('date')
	# 		calender_event=annual_calender()
	# 		calender_event.event=eventname
	# 		date_formatted=datetime.strptime(date, "%Y-%m-%d").date()
	# 		datetime_final=datetime.combine(date_formatted, datetime.min.time())
	# 		calender_event.date=timezone.make_aware(datetime_final, timezone.get_current_timezone())
	# 		calender_event.tenant=request.user.tenant	
	# 		calender_event.save()
	# 	if (calltype == 'event'):
	# 		events = annual_calender.objects.for_tenant(request.user.tenant).all()
	# 		for event in events:
	# 			response_data.append({'title':event.event, 'start': localtime(event.date).isoformat(), 'allDay':True})
	# 	jsondata = json.dumps(response_data)
	# 	return HttpResponse(jsondata)
	return render (request, 'library/book_issue.html',{'books':books, 'classlist':classlist})