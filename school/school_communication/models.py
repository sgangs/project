from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User
from school_teacher.models import Teacher
from school_student.models import Student



visible_to_choices=((1,'Student'),
		(2,'Parent'),
		(3,'Both'))

#This model is to store one to one comments by teacher/staff on students
class student_remark(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentRemark_classadmin_student_student')	
	visible_to=models.PositiveSmallIntegerField(choices=visible_to_choices)
	remarked_by=models.ForeignKey(Teacher,db_index=True,related_name='studentRemarkBy_classadmin_teacher_teacher')	
	comment=models.TextField()
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentRemark_classadmin_user_tenant')
	objects=TenantManager()

	# class Meta:
	# 	unique_together = (("final_report","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.remarked_by)


commentor_type_choices=(('Master','Master'),
			('Teacher','Teacher'),
			('Admin','Admin'),
			('Principal','Principal'),
			('Account','Account'),			
			('Collector','Fee Collector'),
			('Student','Student'),
			('Parent','Parent'))

class student_remark_comment(models.Model):
	id=models.BigAutoField(primary_key=True)
	remark=models.ForeignKey(student_remark, db_index=True,related_name='studentRemarkComment_studentRemark')
	commented_by=models.ForeignKey(User,db_index=True,related_name='studentRemarkCommentBy_classadmin_student_student')	
	commentor_type=models.CharField(max_length=10,choices=commentor_type_choices)
	comment=models.TextField()
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentRemarkComment_classadmin_user_tenant')
	objects=TenantManager()

	# class Meta:
	# 	unique_together = (("final_report","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.commented_by)
