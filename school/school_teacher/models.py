import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User
#from school_genadmin.models import Branch
from school_genadmin.models import Subject, class_group

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

gender_list=(('M','Male'),
				('F','Female'),
				('O','Other'),)

staff_type=(('Teacher','Teacher'),
				('Admin','Admin'),
				('Principal','Principal'),
				('Accounts','Accounts'),
				('Collector','Fee Collector'))

blood_list=(('A+','A Positive'),
				('B+','B Positive'),
				('O+','O Positive'),
				('AB+','AB Positive'),
				('A-','A Negative'),
				('B-','B Negative'),
				('O-','O Negative'),
				('AB-','AB Negative'),
				('O','Other'),)

#This is the branch details
class Teacher(models.Model):
	id=models.BigAutoField(primary_key=True)
	first_name=models.CharField(max_length=100)
	last_name=models.CharField(max_length=100)
	dob=models.DateField("Date of Birth", blank=True, null=True)
	staff_type=models.CharField(max_length=12,choices=staff_type)
	joining_date=models.DateField(blank=True, null=True)
	key=models.CharField(db_index=True,max_length=12)
	gender=models.CharField(max_length=1,choices=gender_list)
	blood_group=models.CharField('Blood Group', max_length=3,choices=blood_list, blank=True, null=True)
	local_id=models.CharField("School teacher ID",blank=True,null=True, max_length=20)
	slug=models.SlugField(max_length=32)
	contact=models.CharField('Phone Number',max_length=13,blank=True, null=True)
	#contact_2=models.CharField(max_length=13, blank=True, null=True)
	email_id=models.EmailField(blank=True, null=True)
	user=models.ForeignKey(User,db_index=True,blank=True, null=True,related_name='teacher_teacher_user_user')
	address_line_1=models.TextField("Address Line 1",blank=True, null=True)
	address_line_2=models.TextField("Address Line 2",blank=True, null=True)
	state=models.CharField(blank=True, null=True,max_length=30)
	pincode=models.PositiveIntegerField(blank=True, null=True)
	#subject = models.ManyToManyField(Subject)
	#class_group = models.ManyToManyField(class_group)
	#branch=models.ForeignKey(Branch,db_index=True,related_name='teacher_schoolTeacher_genadmin_branch')
	tenant=models.ForeignKey(Tenant,db_index=True,null=True,related_name='teacher_teacher_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="te"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_teacher_number='001'
			last_teacher=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_teacher:
				last_teacher_number=int(last_teacher.key[8:])
				next_teacher_number='{0:03d}'.format(last_teacher_number + 1)
			self.key=data+today_string+next_teacher_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(Teacher, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s' % (self.key, self.first_name, self.last_name)

class teacher_history(models.Model):
	id=models.BigAutoField(primary_key=True)
	teacher=models.ForeignKey(Teacher,db_index=True, related_name='teacherHistory_teacher')
	work_place=models.TextField()
	details=models.TextField(blank=True,null=True)
	reward=models.TextField(blank=True, null=True)

class teacher_education(models.Model):
	id=models.BigAutoField(primary_key=True)
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='teacherEducation_teacher')
	degree_name=models.TextField()
	institute=models.TextField()
	details=models.TextField(blank=True, null=True)
	reward=models.TextField(blank=True, null=True)