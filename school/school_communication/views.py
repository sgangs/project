from datetime import date, datetime
import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import *
from school_teacher.models import Teacher
from school_student.models import Student
from school_eduadmin.models import classstudent


@login_required
#This view is not for owner. Onlt for staffs.
def write_remark(request):
	this_tenant=request.user.tenant
	year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
	staff=Teacher.objects.get(user=request.user)
	if request.method == 'POST':
		calltype = request.POST.get('calltype')
		response_data=[]
		if calltype=='class':
			class_selected = request.POST.get('classsection')
			students_list=classstudent.objects.for_tenant(request.user.tenant).\
				filter(class_section=class_selected,year=year).select_related("student")
			for student in students_list:
				response_data.append({'data_type':'Student','id':student.student.id,'roll_no': student.roll_no,\
					'first_name': student.student.first_name, 'last_name': student.student.last_name})
		elif calltype=='save':
			studentid = request.POST.get('studentid')
			comment = request.POST.get('comment')
			new_remark=student_remark()
			new_remark.student=Student.objects.for_tenant(this_tenant_.get(id=studentid))
			new_remark.visible_to=3
			new_remark.remarked_by=staff
			new_remark.comment=comment
			new_remark.tenant=this_tenant
			new_remark.save()
	remarks=student_remark.objects.for_tenant(this_tenant).filter(remarked_by=staff).\
			prefetch_related("studentRemarkComment_studentRemark")
	classes = class_section.objects.for_tenant(this_tenant).values('id','name')
	return render (request, 'classadmin/student_remarks.html', {'classes':classes,'remarks':remarks})