from decimal import Decimal
from datetime import date, datetime
import json
from dateutil.rrule import *
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.timezone import localtime
from num2words import num2words

from .models import cadre_leave, staff_cadre, leave_type, teacher_attendance
from school_genadmin.models import annual_calender
from school_teacher.models import Teacher
from .models import staff_cadre_linking, cadre_leave, staff_leave
from school_genadmin.genadmin_util import holiday_calculator


def create_staff_cadre_link(request):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            year=int(request.POST.get('year'))
            cadreid=int(request.POST.get('cadre'))
            cadre=staff_cadre.objects.for_tenant(this_tenant).get(id=cadreid)
            teachers=json.loads(request.POST.get('details'))
            response_data=[]
            print (year)
            try:
                cadre_leave_details_all=cadre_leave.objects.for_tenant(this_tenant).filter(cadre=cadre, year=year).all()
                create_leave=True
            except:
                create_leave=False
            for data in teachers:
                teacherid=data['teacherid']
                teacher=Teacher.objects.for_tenant(this_tenant).get(id=teacherid)
                linking=staff_cadre_linking()
                linking.cadre=cadre
                linking.teacher=teacher
                linking.cadre_type='Teacher'
                linking.year=year
                linking.tenant=this_tenant
                linking.save()
                if create_leave:
                    for details in cadre_leave_details_all:
                        create_leave_staff_link_from_staff(request, details.id, teacher)
        except:
            transaction.rollback()


#This function is used to link cadre and leave types and set number to these leave types per cadre 
def create_leave_cadre_link(request):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            year=int(request.POST.get('year'))
            leave_lists=json.loads(request.POST.get('details'))
            response_data=[]
            for data in leave_lists:
                cadreid=data['cadreid']
                leaveid=data['leaveid']
                numbers=float(data['numbers'])
                cadre=staff_cadre.objects.for_tenant(this_tenant).get(id=cadreid)
                leave=leave_type.objects.for_tenant(this_tenant).get(id=leaveid)
                linking=cadre_leave()
                linking.cadre=cadre
                linking.leave_type=leave
                linking.year=year
                linking.numbers=numbers
                linking.tenant=this_tenant
                linking.save()
                create_leave_staff_link_from_cadre(request, linking.id)
                # return 
        except:
            transaction.rollback()

def create_leave_staff_link_from_staff(request, cadre_leave_details_id, staff):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            cadre_leaves=cadre_leave.objects.for_tenant(this_tenant).get(id=cadre_leave_details_id)
            linking=staff_leave()
            linking.teacher=staff
            linking.leave_type=cadre_leaves.leave_type
            linking.year=cadre_leaves.year
            linking.numbers=cadre_leaves.numbers
            linking.tenant=this_tenant
            linking.save()
        except:
            transaction.rollback()

def create_leave_staff_link_from_cadre(request, cadre_leave_details_id):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            cadre_leaves=cadre_leave.objects.for_tenant(this_tenant).get(id=cadre_leave_details_id)
            cadre=staff_cadre.objects.for_tenant(this_tenant).get(id=cadre_leaves.cadre.id)
            staffs=staff_cadre_linking.objects.for_tenant(this_tenant).filter(cadre=cadre).all()
            for item in staffs:
                staff=Teacher.objects.for_tenant(this_tenant).get(staffCadreLinking_hr_teacher_teacher=item)
                linking=staff_leave()
                linking.teacher=staff
                linking.leave_type=cadre_leaves.leave_type
                linking.year=cadre_leaves.year
                linking.numbers=cadre_leaves.numbers
                linking.tenant=this_tenant
                linking.save()
        except:
            transaction.rollback()


def teacher_attendance_details(start, end, teacherid):
    response_data={}
    start=datetime.strptime(request.POST.get('start'),"%Y-%m-%d").date()
    end=datetime.strptime(request.POST.get('end'),"%Y-%m-%d").date()
    teacher=students.get(id=teacherid)
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
    hol.sort();
    no_rep.sort();
    for i in attendance:
        dict_attendance =({'data_type':'Report','is_present':i.ispresent, \
            'date': datetime.strftime(i.date, '%d -%m -%Y'), 'remarks':i.remarks})
        response_data['attendance']=dict_attendance
    for i in no_rep:
        no_report=({'data_type':'No Report','date': datetime.strftime(i, '%d -%m -%Y')})
        response_data['no_report']=no_report
    for i in hol:
        holiday=({'data_type':'Holiday','date': datetime.strftime(i, '%d -%m -%Y')})
        response_data['holiday']=holiday

    return response_data