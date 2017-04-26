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
from school_genadmin.models import class_group, academic_year
from school_student.models import Student
from .forms import *
from .models import Book, issue_period


@login_required
#This is used to add new object for library models
def library_new(request, input_type):
	# if (input_type == "Library"):
	# 	importform = LibraryForm
	# 	name='genadmin:subject_list'
	if (input_type == "Book"):
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

@login_required
#This is used to add nes object for library models
def library_edit(request, detail):
	item=get_object_or_404(Book.objects.for_tenant(request.user.tenant), id=detail)
	importform = BookEditForm
	name='library:book_list'
	current_tenant=request.user.tenant
	if (request.method == "POST"):
		form = importform(request.POST, instance=item, tenant=current_tenant)
		if form.is_valid():
			form.save()
			return redirect(name)
	else:
		form=importform(instance=item,tenant=current_tenant)
	# return render(request, 'master/new.html',{'form': form, 'item': item, 'editable': True})
	return render(request, 'library/edit.html',{'form': form, 'item': 'Edit Book Details'})

@login_required
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
def book_issue(request):
	this_tenant=request.user.tenant
	books=Book.objects.for_tenant(this_tenant).filter(quantity_available__gte=0).all()	
	classlist=class_section.objects.for_tenant(this_tenant).all()
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	if request.method == 'POST':
		calltype=request.POST.get('calltype')
		response_data = []
		if (calltype == 'class_student'):
			class_id=request.POST.get('class_id')
			class_selected=classlist.get(id=class_id)
			response_data=list(classstudent.objects.for_tenant(this_tenant).filter(class_section=class_selected, year=year)\
								.select_related('student'))
		if (calltype == 'student_issue'):
			student_id=request.POST.get('student_id')
			remarks=request.POST.get('remarks')
			class_student_selected=classstudent.objects.for_tenant(this_tenant).get(id=student_id)
			student=Student.objects.for_tenant(this_tenant).get(classstudent_eduadmin_student_student=class_student_selected)
			try:
				response_data=list(book_issue.objects.for_tenant(this_tenant).filter(issued_to=student, returned=False).\
								select_related("book").values("book", "issued_on"))
			except:
				response_data['issues']='No issue'
		if (calltype == 'save'):
			class_id=request.POST.get('class_id')
			book_id=request.POST.get('book_id')
			student_id=request.POST.get('student_id')
			issued_date=request.POST.get('issued_date')
			remarks=request.POST.get('remarks')
			class_selected=classlist.get(id=class_id)
			class_student_selected=classstudent.objects.for_tenant(this_tenant).get(id=student_id)
			student=Student.objects.for_tenant(this_tenant).get(classstudent_eduadmin_student_student=class_student_selected)
			book_selected=books.objects.get(id=book_id)
			new_issue=book_issue()
			new_issue.book=book_selected
			new_issue.issued_on=issued_date
			new_issue.issued_to=student
			new_issue.issued_class=class_selected
			new_issue.remark=remark
			new_issue.returned=False
			new_issue.tenant=this_tenant
			new_issue.save()						
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'library/book_issue.html',{'books':books, 'classlist':classlist})

@login_required
def book_return(request):
	this_tenant=request.user.tenant
	issued_books=book_issue.objects.for_tenant(this_tenant).filter(returned=False).select_related('book', 'issued_to','issued_class')
	if request.method == 'POST':
		calltype=request.POST.get('calltype')
		response_data = []
		if (calltype == 'save'):
			return_details =json.loads(request.POST.get('return_details'))
			return_date=request.POST.get('return_date')
			with transaction.atomic():
				try:
					for item in return_details:
						issue_id=item['return_id']
						issue_details=issued_books.get(id=issue_id)
						issue_details.returned=True
						issued_details.returned_on=return_date
						issued_details.save()			
				except:
					transaction.rollback()
		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)
	return render (request, 'library/book_return.html',{'issued':issued_books})