import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant
from school_teacher import Teacher


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#Leave type to be decided by HR
class leave_type(models.Model):
	name=models.TextField()
	key=models.CharField(max_length=5)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='leaveType_hr_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="lt"+" "+self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Attendance, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name","tenant",),("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.key, self.name)


#I am intentioanlly not using django generic models as that is not maintainable

#This is the daily attendance abstract model, only used for code maintainance and doesn't affect db schema
class Attendance(models.Model):
	
	date=models.DateField()#form/datefield option needed as "input_formats=settings.DATE_INPUT_FORMATS"
	ispresent=models.CharField(db_index=True,max_length=12)
	remarks=models.TextField()
	slug=models.SlugField(max_length=50)	

	class Meta:
		abstract = True

	
#This is the daily attendance report for teachers
class teacher_attendance(Attendance):
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='teacherAttendance_hr_teacher_teacher')
	leave_type=models.ForeignKey(leave_type,db_index=True,related_name='teacherAttendance_leaveType')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='teacherAttendance_hr_user_tenant')
	objects=TenantManager()

	def save(self, *args, **kwargs):
		if not self.id:
			item="att"+" "+self.tenant.key+" "+self.teacher.key+" "+str(self.date)
			self.slug=slugify(item)
		super(Attendance, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("teacher", "date","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.teacher, self.date)