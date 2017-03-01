from datetime import date, datetime
from django.db import IntegrityError

from school_user.models import User, Tenant
from school_genadmin.models import class_group, Subject
from school_student.models import Student
from .models import subject_teacher, Syllabus, period, total_period, class_section, classstudent, Term, Exam

def period_add(request, class_selected):
    this_tenant=request.user.tenant
    day=int(request.POST.get('day'))
    period_no=int(request.POST.get('period'))
    year=request.POST.get('year')
    subjectid=request.POST.get('subject')
    class_group=class_selected.classgroup
    subject=Subject.objects.for_tenant(this_tenant).get(id=subjectid)    
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

def get_student_list (request,batch,class_sections):
    this_tenant=request.user.tenant
    response_data=[]
    batchid=request.POST.get('batchid')
    year=int(request.POST.get('year'))
    batch_selected=batch.get(id=batchid)
    excluded_student_raw=classstudent.objects.filter(tenant=this_tenant,year=year).all()
    excluded_student=Student.objects.filter(classstudent_eduadmin_student_student__in=excluded_student_raw).all()
    students=Student.objects.for_tenant(this_tenant).filter(batch=batch_selected).exclude(id__in=excluded_student).all()
    for student in students:
        response_data.append({'data_type':'Student','id':student.id,'key':student.key, \
            'local_id':student.local_id,'name':student.first_name+" "+student.last_name,})
    return response_data

def create_term(name, tenant):
    term_new=Term()
    term_new.name=name
    term_new.tenant=tenant
    term_new.save()

def create_exam(name, key, tenant, weightage=1, term_name=""):
    exam_new=Exam()
    exam_new.name=name
    if (term_name!= ""):
        term=Term.objects.for_tenant(tenant).get(name=term_name)
        exam_new.term=term
    exam_new.key=key
    exam_new.total=100
    exam_new.weightage=weightage
    exam_new.tenant=tenant
    print ("In Create Exam")
    print(key)
    exam_new.save()