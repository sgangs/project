import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant
from school_teacher.models import Teacher


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

leave_choices=(('LOP','Loss of Pay'),
			('O','Others'),)

#Leave type to be decided by HR
class leave_type(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=40)
	key=models.CharField(max_length=5)
	leave_type_option=models.CharField(max_length=3, choices=leave_choices, default="O")
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='leaveType_hr_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="lt"+" "+self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(leave_type, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name","tenant",),("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.key, self.name)

cadre_type=(('Master','Master'),
			('Teacher','Teacher'),
			('Admin','Admin'),
			('Principal','Principal'),
			('Account','Account'),			
			('Collector','Fee Collector'),)


#Create Staff Cadre
class staff_cadre(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=40)
	cadre_type=models.CharField(max_length=10, choices=cadre_type, db_index=True, default='Teacher')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='staffCadre_hr_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("name","tenant"),)
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


#This model links teacher (staff) to cadre
class staff_cadre_linking(models.Model):
	id=models.BigAutoField(primary_key=True)
	cadre=models.ForeignKey(staff_cadre,db_index=True,related_name='staffCadreLinking_staffCadre')
	cadre_type=models.CharField(max_length=10, db_index=True)
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='staffCadreLinking_hr_teacher_teacher')
	year=models.PositiveSmallIntegerField()
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='staffCadreLinking_hr_user_tenant')
	objects=TenantManager()

	class Meta:
		unique_together = (("cadre","teacher","year"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.cadre, self.teacher)

#This model links cadre to leaves and define the number of leaves
class cadre_leave(models.Model):
	id=models.BigAutoField(primary_key=True)
	cadre=models.ForeignKey(staff_cadre,db_index=True,related_name='cadreLeave_staffCadre')
	leave_type=models.ForeignKey(leave_type, related_name='cadreLeave_leaveType')
	year=models.PositiveSmallIntegerField("Please enter (year for) start of the academic year")
	numbers=models.PositiveSmallIntegerField()
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='cadreLeave_hr_user_tenant')
	objects=TenantManager()

	class Meta:
		unique_together = (("cadre","leave_type","year",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.cadre, self.teacher)

#This model links cadre to leaves and define the number of leaves
class staff_leave(models.Model):
	id=models.BigAutoField(primary_key=True)
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='staffLeave_hr_teacher_teacher')
	leave_type=models.ForeignKey(leave_type, related_name='staffLeave_leaveType')
	year=models.PositiveSmallIntegerField("Please enter start (year) of the academic year")
	numbers=models.PositiveSmallIntegerField()
	leaves_taken=models.PositiveSmallIntegerField(default=0)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='staffLeave_hr_user_tenant')
	objects=TenantManager()

	class Meta:
		unique_together = (("teacher","leave_type","year",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.cadre, self.teacher)



attendance_choices=((1,'Normal'),
			(2,'Mispunch'),)

class teacher_attendance(models.Model):
	id=models.BigAutoField(primary_key=True)
	date=models.DateField(db_index=True)#form/datefield option needed as "input_formats=settings.DATE_INPUT_FORMATS"
	ispresent=models.BooleanField()
	is_authorized=models.BooleanField(default=True)
	attendance_type=models.PositiveSmallIntegerField(choices=attendance_choices, default=1)
	remarks=models.TextField()
	# slug=models.SlugField(max_length=50)
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='teacherAttendance_hr_teacher_teacher')
	leave_type=models.ForeignKey(leave_type, blank=True, null=True, related_name='teacherAttendance_leaveType')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='teacherAttendance_hr_user_tenant')
	objects=TenantManager()

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item="att"+" "+self.tenant.key+" "+self.teacher.key+" "+str(self.date)
	# 		self.slug=slugify(item)
	# 	super(teacher_attendance, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("teacher", "date","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.teacher, self.date)