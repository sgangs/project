from datetime import date, datetime
from django.db import IntegrityError

from school_user.models import User, Tenant
from school_genadmin.models import class_group, Subject
from school_student.models import Student
from school_fees.models import student_fee, group_default_fee
from .models import subject_teacher, period, total_period, class_section, classstudent, Term, Exam, grade_table
                # Syllabus

def period_add(request, class_selected):
    this_tenant=request.user.tenant
    day=int(request.POST.get('day'))
    period_no=int(request.POST.get('period'))
    year=request.POST.get('year')
    subjectid=request.POST.get('subject')
    class_group=class_selected.classgroup
    subject=Subject.objects.for_tenant(this_tenant).get(id=subjectid)    
    # try:
    #     class_syllabus=Syllabus.objects.for_tenant(this_tenant).filter(class_group=class_group,year=year,subject=subject)
    # except:
    #     return "Error"
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
    excluded_student_raw=classstudent.objects.filter(tenant=this_tenant).all()
    excluded_student=Student.objects.filter(classstudent_eduadmin_student_student__in=excluded_student_raw).all()
    students=Student.objects.for_tenant(this_tenant).filter(batch=batch_selected, isactive=True).\
                order_by('first_name','last_name').exclude(id__in=excluded_student).all()
    i=0
    for student in students:
        i+=1
        if (i<2000):
            response_data.append({'data_type':'Student','id':student.id,'key':student.key, \
                'local_id':student.local_id,'name':student.first_name+" "+student.last_name,})
        else:
            break
    return response_data

def create_term(name, year, tenant):
    term_new=Term()
    term_new.name=name
    term_new.year=year
    term_new.tenant=tenant
    term_new.save()

def create_exam(name, key, sl_no, year, tenant, term_name, exam_type, class_group=[], weightage=100):
    exam_new=Exam()
    exam_new.name=name
    if (term_name!= ""):
        term=Term.objects.for_tenant(tenant).get(name=term_name)
        exam_new.term=term
    exam_new.key=key
    exam_new.serial_no = sl_no
    exam_new.year=year
    exam_new.total=100
    exam_new.weightage=weightage
    exam_new.tenant=tenant
    exam_new.save()

def create_grade_table (grade_type,sl_no,max_mark,min_mark, grade, grade_point, this_tenant):
    new_table=grade_table()
    new_table.grade_type=grade_type
    new_table.sl_no=sl_no
    new_table.min_mark=min_mark
    new_table.max_mark=max_mark
    new_table.grade=grade
    new_table.grade_point=grade_point
    new_table.tenant=this_tenant
    new_table.save()

def student_add_fee(student, class_selected, year, this_tenant):
    class_group=class_selected.classgroup
    try:
        group_fee=group_default_fee.objects.for_tenant(this_tenant).get(classgroup=class_group, year=year)
        proceed=True
    except:
        proceed=False
    if (proceed):
        new_fee=student_fee()
        new_fee.student=student
        new_fee.year=year
        # new_fee.monthly_fee=group_fee.monthly_fee
        new_fee.tenant=this_tenant
        new_fee.save()
        generic_fees=group_fee.generic_fee.all()
        for fee in generic_fees:
            new_fee.generic_fee.add(fee)