from .models import Attendance
#from school_eduadmin.models import * #class_section
from school_teacher.models import Teacher
from school_student.models import Student
from school_eduadmin.models import class_section, classstudent, Exam, Syllabus
from school_genadmin.models import class_group, Subject 

#This function is used to provide students' data for attendance/exam score entry
def get_student_data(request, called_for, classes ):
    classid=request.POST.get('classid')
    if (called_for=='Attendance'):
    	year=request.POST.get('year')
    else:
    	examid=int(request.POST.get('examid'))
    	year=Exam.objects.for_tenant(request.user.tenant).get(id__exact=examid).year
    class_selected=classes.get(id__exact=classid)
    response_data=[]
    # try:
    students_list=classstudent.objects.for_tenant(request.user.tenant).\
    	filter(class_section=class_selected,year=year).select_related("student")
    for student in students_list:
    	response_data.append({'data_type':'Student','id':student.student.id,'key':student.student.key,\
    			'local_id': student.student.local_id,'first_name': student.student.first_name, 'last_name': student.student.last_name})
    if (called_for=='Attendance'):
    	return response_data
    else:
    	class_group=class_selected.classgroup
    	subjects=Syllabus.objects.filter(class_group=class_group, year=year).select_related("subject")
    	for subject in subjects:
    		response_data.append({'data_type':'Subject','id':subject.subject.id,'name':subject.subject.name})
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
 	#try:
 	for data in attendance_list:
 		response_data.append({'data_type':'Attendance','id':data.student.id,'key':data.student.key,\
 				'local_id': data.student.local_id,'first_name': data.student.first_name, 'last_name': data.student.last_name,\
 				'is_present': data.ispresent, 'remarks':data.remarks})
 		return response_data
 	# except:
 	# 	pass

