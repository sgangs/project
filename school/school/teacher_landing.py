from datetime import datetime, date, timedelta
from dateutil.rrule import *
from dateutil.parser import *
# from functools import wraps
# from django.db.models import Sum
# from django.shortcuts import redirect, resolve_url

from school_genadmin.genadmin_util import holiday_calculator
from school_user.models import User, Tenant
from school_teacher.models import Teacher
from school_genadmin.models import annual_calender
from school_eduadmin.models import class_section, classteacher, subject_teacher 
from school_hr.models import teacher_attendance

def get_class_teacher(request, teacher, year, this_tenant):
    classes=list(classteacher.objects.for_tenant(this_tenant).filter(class_teacher=teacher, year=year))
    return classes

def get_subject_teacher(request, teacher, year, this_tenant):
    
    subjects=list(subject_teacher.objects.for_tenant(this_tenant).filter(teacher=teacher, year=year))
    return subjects

def staff_attendance_number(request, teacher, this_tenant):
	start=date.today() - timedelta(days=30)
	end=date.today()
	response_data=[]
	attendance=teacher_attendance.objects.filter(teacher=teacher, date__range=(start,end))
	attendace_dates=[]
	for i in attendance:
		attendace_dates.append(datetime.strptime(datetime.strftime(i.date,'%Y %m %d'), '%Y %m %d'))
	total=list(rrule(DAILY, dtstart=start, until=end))
	events= annual_calender.objects.filter(date__range=(start,end))
	events_hol=events.filter(attendance_type=2)
	hol=[]
	for event in events_hol:
		hol.append(datetime.strptime(datetime.strftime(event.date,'%Y %m %d'), '%Y %m %d'))
	hol=holiday_calculator(start, end, events, hol)
	total_working=list(set(total) -set(hol))
	no_rep=list(set(total_working)-set(attendace_dates))
	total_present=attendance.filter(ispresent=True, is_authorized=True).count()
	yet_authorize=attendance.filter(is_authorized=False).count()
	no_attendance=len(no_rep)
	total_working=len(total_working)
	per_present=round(total_present/total_working*100)
	per_no=round(no_attendance/total_working*100)
	per_pending=round(yet_authorize/total_working*100)
	# for i in attendance:
	# 	if i.is_present:
	# 		is_present+=1		
	# for i in no_rep:
	# 	no_attendance+=1
	response_data.append({"present":total_present,"per_present":per_present, "no_attendance": no_attendance,"per_no":per_no, \
							"pending_authorize": yet_authorize,"per_pending":per_pending, "total":total_working})
	return(response_data)
	