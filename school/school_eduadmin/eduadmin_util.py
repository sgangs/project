from datetime import date, datetime
from django.db import IntegrityError

from school_user.models import User, Tenant
from school_genadmin.models import class_group, Subject
from .models import subject_teacher, Syllabus, period, total_period, class_section

def period_add(request, class_selected):
    this_tenant=request.user.tenant
    day=int(request.POST.get('day'))
    period_no=int(request.POST.get('period'))
    year=request.POST.get('year')
    subjectid=request.POST.get('subject')
    class_group=class_selected.classgroup
    subject=Subject.objects.get(id=subjectid)    
    try:
        class_syllabus=Syllabus.objects.for_tenant(this_tenant).filter(class_group=class_group,year=year,subject=subject)
    except:
        return "Error"
    try:
        teacher=subject_teacher.objects.get(class_section=class_selected,subject=subject,year=year).teacher
    except:
        return "Subject teacher doesn't exist"
    new_period=period()
    new_period.day=day
    new_period.period=period_no
    new_period.year=year
    new_period.class_section=class_selected
    new_period.subject=subject
    new_period.teacher=teacher
    new_period.tenant=this_tenant
    new_period.save()
