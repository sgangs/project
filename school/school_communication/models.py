from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


# visible_to_choices=((1,'Student'),
# 		(2,'Parent'),
# 		(3,'Both'))

# #This model is to store one to one comments by teacher/staff on students
# class student_remark(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	student=models.ForeignKey(Student,db_index=True,related_name='studentRemark_communication_student_student')	
# 	visible_to=models.PositiveSmallIntegerField(choices=visible_to_choices)
# 	remarked_by=models.ForeignKey(Teacher,db_index=True,related_name='studentRemarkBy_communication_teacher_teacher')	
# 	comment=models.TextField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentRemark_communication_user_tenant')
# 	objects=TenantManager()

# 	# class Meta:
# 	# 	unique_together = (("final_report","subject","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.remarked_by)


# commentor_type_choices=(('Master','Master'),
# 			('Teacher','Teacher'),
# 			('Admin','Admin'),
# 			('Principal','Principal'),
# 			('Account','Account'),			
# 			('Collector','Fee Collector'),
# 			('Student','Student'),
# 			('Parent','Parent'))

# class student_remark_comment(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	remark=models.ForeignKey(student_remark, db_index=True,related_name='studentRemarkComment_studentRemark')
# 	commented_by=models.ForeignKey(User,db_index=True,related_name='studentRemarkCommentBy_communication_user_user')	
# 	commentor_type=models.CharField(max_length=10,choices=commentor_type_choices)
# 	comment=models.TextField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentRemarkComment_communication_user_tenant')
# 	objects=TenantManager()

# 	# class Meta:
# 	# 	unique_together = (("final_report","subject","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.commented_by)


# class remark(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	visible_to=models.PositiveSmallIntegerField(choices=commentor_type_choices)
# 	remarked_by=models.ForeignKey(User,db_index=True,related_name='remark_communication_user_user')	
# 	comment=models.TextField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='remark_communication_user_tenant')
# 	objects=TenantManager()

# 	# class Meta:
# 	# 	unique_together = (("final_report","subject","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.remarked_by)


# class remark_comment(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	remark=models.ForeignKey(student_remark, db_index=True,related_name='remarkComment_remark')
# 	commented_by=models.ForeignKey(User,db_index=True,related_name='remarkCommentBy_communication_user_user')	
# 	commentor_type=models.CharField(max_length=10,choices=commentor_type_choices)
# 	comment=models.TextField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='remarkComment_communication_user_tenant')
# 	objects=TenantManager()

# 	# class Meta:
# 	# 	unique_together = (("final_report","subject","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.commented_by)

class from_communication(models.Model):
	id=models.BigAutoField(primary_key=True)
	subject=models.TextField()
	body=models.TextField()
	from_user=models.ForeignKey(User,db_index=True,related_name='fromCommunication_communication_user_user')
	sent_on=models.DateTimeField(auto_now_add=True)
	sent=models.BooleanField(default=False)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='fromCommunication_communication_user_tenant')
	objects=TenantManager()

	# class Meta:
	# 	unique_together = (("final_report","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.from_user)


class to_comminucation(models.Model):
	id=models.BigAutoField(primary_key=True)
	from_mail=models.ForeignKey(from_communication,db_index=True,related_name='toCommunication_fromCommunication')
	to_user=models.ForeignKey(User,db_index=True,related_name='toCommunication_communication_user_user')
	received_on=models.DateTimeField(auto_now_add=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='toCommunication_communication_user_tenant')
	objects=TenantManager()

	# class Meta:
	# 	unique_together = (("final_report","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.to_user)