import datetime as dt
from datetime import datetime
from django.db import models
#from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User
from school_eduadmin.models import Exam, class_section, Term
from school_genadmin.models import Subject
from school_teacher.models import Teacher
from school_student.models import Student


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the daily attendance report
class Attendance(models.Model):
	id=models.BigAutoField(primary_key=True)
	class_section=models.ForeignKey(class_section, related_name='attendance_classadmin_eduadmin_classSection')
	student=models.ForeignKey(Student,db_index=True,related_name='attendance_classadmin_student_student')
	has_applied_leave=models.NullBooleanField() #Has the student applied for leave?
	date=models.DateField()
	ispresent=models.CharField(db_index=True,max_length=12)
	remarks=models.TextField(blank=True, null=True)
	student_remarks=models.TextField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='attendance_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("student", "date","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.student, self.date)


#This is the exam report. Add marks for each student, subject wise. Hidden fields, except slug hs to be incorporated
class exam_report(models.Model):
	id=models.BigAutoField(primary_key=True)
	class_section=models.ForeignKey(class_section,related_name='examReport_classadmin_eduadmin_classSection')
	exam=models.ForeignKey(Exam,db_index=True,related_name='examReport_classadmin_eduadmin_exam')
	subject=models.ForeignKey(Subject,db_index=True,related_name='examReport_classadmin_genadmin_subject')
	# is_approved=models.BooleanField(default=False)
	student=models.ForeignKey(Student,db_index=True,related_name='examReport_classadmin_student_student')
	year=models.PositiveSmallIntegerField(db_index=True)
	final_score=models.DecimalField(max_digits=5, decimal_places=2, default=0)
	grade=models.CharField(max_length=4,blank=True, null=True)
	grade_point=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	remarks=models.TextField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='examReport_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("student","exam","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.student, self.exam)

topics=(('Life','2(A) Life Skills'),
		('Work','2(B) Work Education'),
		('VPA','2(C) Visual & Performing Art'),
		('AV','2(D) Attitude & Values'),
		('CSA','3(A) Co-Scholastic Actitivies'),
		('HPE','3(B) Health & Physical Education'))

#Co Scholastic Report
class exam_coscholastic_report(models.Model):
	id=models.BigAutoField(primary_key=True)
	class_section=models.ForeignKey(class_section,related_name='examCoscholasticReport_classadmin_eduadmin_classSection')
	exam=models.ForeignKey(Exam,db_index=True,related_name='examCoscholasticReport_classadmin_eduadmin_exam')
	term=models.ForeignKey(Term,db_index=True,related_name='examCoscholasticReport_classadmin_eduadmin_Term')
	details=models.TextField(blank=True)
	sl_no=models.PositiveSmallIntegerField()
	student=models.ForeignKey(	Student,db_index=True,related_name='examCoscholasticReport_classadmin_student_student')
	topic=models.TextField() #The topics are listed, but can also be entered by user.
	total=models.PositiveSmallIntegerField(blank=True, null=True)
	grade=models.CharField(max_length=4,blank=True, null=True)
	grade_point=models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
	remarks=models.TextField(blank=True, null=True)
	# year=models.PositiveSmallIntegerField(db_index=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='examCoscholasticReport_classadmin_user_tenant')
	objects=TenantManager()

	class Meta:
		unique_together = (("student","exam","topic","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.student, self.exam)

# class exam_final_report(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	year=models.PositiveSmallIntegerField(db_index=True)
# 	class_section=models.ForeignKey(class_section,related_name='examFinalReport_classadmin_eduadmin_classSection')
# 	student=models.ForeignKey(	Student,db_index=True,related_name='examFinalReport_classadmin_student_student')
# 	remarks=models.TextField()
# 	passed=models.BooleanField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='examFinalReport_classadmin_user_tenant')
# 	objects=TenantManager()

# 	class Meta:
# 		unique_together = (("student","year","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s %s' % (self.student, self.year)


class term_report(models.Model):
	class_section=models.ForeignKey(class_section,related_name='termReport_classadmin_eduadmin_classSection')
	student=models.ForeignKey(Student,db_index=True,related_name='termReport_classadmin_student_student')
	term=models.ForeignKey(Term, related_name='termReport_classadmin_eduadmin_term')
	subject=models.ForeignKey(Subject,db_index=True,related_name='termReport_classadmin_genadmin_subject')
	year=models.PositiveSmallIntegerField(db_index=True)
	term_score=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	term_grade=models.CharField(max_length=4,blank=True, null=True)
	term_grade_point=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='termReport_classadmin_user_tenant')
	objects=TenantManager()

	class Meta:
		unique_together = (("term","subject","year","tenant",))
		# ordering = ('name',)

	# def __str__(self):
	# 	return '%s %s' % (self.student, self.exam)

#Homework details.
class Homework(models.Model):
	id=models.BigAutoField(primary_key=True)
	class_section=models.ForeignKey(class_section,related_name='Homework_classadmin_eduadmin_classSection')
	subject=models.ForeignKey(Subject,related_name='Homework_classadmin_genadmin_subject')
	homework_details=models.TextField()
	date=models.DateField()
	key=models.CharField(db_index=True,max_length=12)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='Homework_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s %s' % (self.class_section, self.subject, self.date)