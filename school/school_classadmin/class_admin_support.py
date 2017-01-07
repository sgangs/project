from django.db.models import Avg
from django.shortcuts import get_object_or_404
from .models import Attendance, exam_report
#from school_eduadmin.models import * #class_section
from school_teacher.models import Teacher
from school_student.models import Student
from school_eduadmin.models import class_section, classstudent, Exam, Syllabus
from school_genadmin.models import class_group, Subject 


#This function is used to provide students' data for attendance/exam score entry
def get_subject_data(request, called_for, classes):
    classid=request.POST.get('classid')
    examid=int(request.POST.get('examid'))
    year=Exam.objects.for_tenant(request.user.tenant).get(id__exact=examid).year
    class_selected=classes.get(id__exact=classid)
    response_data=[]
    try:
        class_group=class_selected.classgroup
        subjects=Syllabus.objects.filter(class_group=class_group, year=year).select_related("subject")
        for subject in subjects:
            response_data.append({'data_type':'Subject','id':subject.subject.id,'name':subject.subject.name})
        return response_data
    except:
      pass

def get_student_data(request, called_for, classes ):
    classid=request.POST.get('classid')
    if (called_for=='Attendance'):
    	year=request.POST.get('year')
    else:
        examid=int(request.POST.get('examid'))
        exam=Exam.objects.for_tenant(request.user.tenant).get(id__exact=examid)
        year=exam.year
        subjectid=int(request.POST.get('subjectid'))
        subject=Subject.objects.get(id=subjectid)
    class_selected=classes.get(id__exact=classid)
    response_data=[]
    # try:
    if (called_for=='Attendance'):
        students_list=classstudent.objects.for_tenant(request.user.tenant).\
    	   filter(class_section=class_selected,year=year).select_related("student")
    else:
        # try:
        excluded_student_raw=exam_report.objects.filter(class_section=class_selected,exam=exam,subject=subject).all()
        excluded_student=Student.objects.filter(examReport_classadmin_student_student__in=excluded_student_raw).all()
        students_list=classstudent.objects.for_tenant(request.user.tenant).\
                filter(class_section=class_selected,year=year).all().exclude(student__in=excluded_student).select_related("student")
        # except:
        #     students_list=classstudent.objects.for_tenant(request.user.tenant).\
        #         filter(class_section=class_selected,year=year).select_related("student")

    for student in students_list:
    	response_data.append({'data_type':'Student','id':student.student.id,'key':student.student.key,\
    			'local_id': student.student.local_id,'first_name': student.student.first_name, 'last_name': student.student.last_name})
    return response_data
    # except:
   	# 	pass

#This function is used to provide data for students' attendance view
def get_attendance_data(request):
    classid=request.POST.get('classid')
    date=request.POST.get('date')
    class_selected=class_section.objects.for_tenant(request.user.tenant).get(id__exact=classid)
    attendance_list=Attendance.objects.filter(class_section=class_selected, date=date)
    response_data=[]
    try:
        for data in attendance_list:
            response_data.append({'data_type':'Attendance','id':data.student.id,'key':data.student.key,\
     				'local_id': data.student.local_id,'first_name': data.student.first_name, 'last_name': data.student.last_name,\
     				'is_present': data.ispresent, 'remarks':data.remarks})
        return response_data
    except:
        pass

def get_exam_report(request, called_for, classes ):
    classid=int(request.POST.get('classid'))
    examid=int(request.POST.get('examid'))
    subjectid=int(request.POST.get('subjectid'))
    exam=Exam.objects.for_tenant(request.user.tenant).get(id__exact=examid)
    class_selected=classes.get(id__exact=classid)
    subject=Subject.objects.get(id=subjectid)
    exam_report_details=exam_report.objects.filter(exam=exam, class_section=class_selected, subject=subject).\
                        select_related('student').all()
    average=exam_report_details.aggregate(Avg('final_score'))
    average_external=exam_report_details.aggregate(Avg('external_score'))
    try:
        average=round(average['final_score__avg'],2)
        response_data=[]
        if (average_external['external_score__avg'] != None):
            for report in exam_report_details:
                response_data.append({'data_type':'Report w ext','score': report.final_score,'internal': report.internal_score,\
                'average':average,'external':report.external_score,\
                'first_name': report.student.first_name, 'last_name': report.student.last_name})
        else:
            for report in exam_report_details:
                response_data.append({'data_type':'Report w.o. ext','score': report.final_score,'internal': report.internal_score,\
                'average':average,'first_name': report.student.first_name, 'last_name': report.student.last_name})
        return response_data
    except:
        pass

#This function is used to provide individual student's data for attendance
def get_studentattendance_data(request, called_for, classes):
    classid=int(request.POST.get('classid'))
    studentid=int(request.POST.get('studentid'))
    date=request.POST.get('date')
    class_selected=classes.get(id__exact=classid)
    student=Student.objects.get(id=studentid)
    response_data=[]
    # try:
    attendance=Attendance.objects.filter(class_section=class_selected, student=student).get(date=date)
    response_data.append({'is_present':attendance.ispresent, 'remarks':attendance.remarks,'id':attendance.id})
    return response_data
    # except:
    #   pass