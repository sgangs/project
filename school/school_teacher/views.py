#from functools import partial, wraps
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required
#from django.db import IntegrityError, transaction
#from django.db.models import Prefetch
#from django.forms.formsets import formset_factory
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
#from django.db.models import F


from school_user.models import Tenant
from .forms import TeacherForm
from .models import Teacher


@login_required
#This is the base page.
def teacher_student_base(request):
	return render (request, 'teacher/teacher_student_base.html')

@login_required
#This is the base page.
def teacher_base(request):
	return render (request, 'teacher/teacher_base.html')

@login_required
#This function helps in addidng new syllabus and exams
def teacherprofile_new(request, input_type):
	if (input_type=="Teacher"):
		importform=TeacherForm
		name='genadmin:unit_list'
	# elif (input_type=="Guardian"):
	# 	importform=StudentGuardianForm
	# 	name='genadmin:unit_list'
	# elif (input_type=="Education"):
	# 	importform=StudentEducationForm
	# 	name='genadmin:unit_list'
	current_tenant=request.user.tenant
	form=importform(tenant=current_tenant)
	if (request.method == "POST"):
		current_tenant=request.user.tenant
		form = importform(request.POST, tenant=current_tenant)
		if form.is_valid():
			item=form.save(commit=False)			
			item.tenant=current_tenant
			item.save()
			return redirect(name)
	return render(request, 'genadmin/new.html',{'form': form, 'item': input_type})
