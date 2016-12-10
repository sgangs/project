import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User
#from school_genadmin.models import Branch
from school_genadmin.models import Subject

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the branch details
class Student(models.Model):
	first_name=models.CharField(max_length=100)
	last_name=models.CharField(max_length=100)
	key=models.CharField(db_index=True,max_length=12)
	slug=models.SlugField(max_length=32)
	contact=models.CharField(max_length=13)
	local_id=models.CharField("Local ID",blank=True,null=True, max_length=50)
	user=models.ForeignKey(User,blank=True, null=True,db_index=True,related_name='student_student_user_user')
	address_line_1=models.TextField("Address Line 1",blank=True, null=True)
	address_line_2=models.TextField("Address Line 2",blank=True, null=True)
	state=models.CharField(blank=True, null=True, max_length=30)
	pincode=models.PositiveIntegerField(blank=True, null=True)
	#subject = models.ManyToManyField(Subject)
	#branch=models.ForeignKey(Branch,db_index=True,related_name='teacher_schoolTeacher_genadmin_branch')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='student_student_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="st"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_student_number='001'
			last_student=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_student:
				last_student_number=int(last_student.key_id[8:])
				next_student_number='{0:03d}'.format(last_student_number + 1)
			self.key=data+today_string+next_student_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(Student, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.first_name, self.last_name)

class student_guardian(models.Model):
	student=models.ForeignKey(Student,db_index=True,related_name='studentGuardian_student')
	relation=models.CharField(max_length=100)
	first_name=models.CharField(max_length=100)
	last_name=models.CharField(max_length=100)
	contact=models.CharField(max_length=13)
	address=models.TextField(blank=True, null=True)
	qualification=models.TextField(blank=True, null=True)
	profession=models.TextField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,null=True,related_name='studentGuardian_student_user_tenant')
	objects=TenantManager()
	class Meta:
		unique_together = (("student","relation", "tenant"))

class student_education(models.Model):
	student=models.ForeignKey(Student,db_index=True,related_name='studentEducation_student')
	degree_name=models.TextField()
	institute=models.TextField()
	details=models.TextField(blank=True, null=True)
	reward=models.TextField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentEducation_student_user_tenant')
	objects=TenantManager()
	class Meta:
		unique_together = (("student", "degree_name"))
