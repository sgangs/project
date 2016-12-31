import datetime as dt
from datetime import datetime
from django.db import models
#from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant, User
from school_eduadmin.models import Exam, class_section, Examiner
from school_genadmin.models import Subject
from school_teacher.models import Teacher
from school_student.models import Student


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the daily attendance report
class Attendance(models.Model):
	class_section=models.ForeignKey(class_section,\
									db_index=True,related_name='attendance_classadmin_eduadmin_classSection')
	student=models.ForeignKey(Student,db_index=True,related_name='attendance_classadmin_student_student')
	date=models.DateField()#form/datefield option needed as "input_formats=settings.DATE_INPUT_FORMATS"
	ispresent=models.CharField(db_index=True,max_length=12)
	remarks=models.TextField()
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='attendance_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="att"+" "+self.tenant.key+" "+self.student.key+" "+str(self.date)
			self.slug=slugify(item)
		super(Attendance, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("student", "date","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.student, self.date)


#This is the exam report. Add marks for each student, subject wise
class exam_report(models.Model):
	class_section=models.ForeignKey(class_section,db_index=True,related_name=\
									'examReport_classadmin_eduadmin_classSection')
	exam=models.ForeignKey(Exam,db_index=True,related_name='examReport_classadmin_eduadmin_exam')
	examiner =models.ForeignKey(Examiner,blank=True, null=True, related_name='examReport_classadmin_eduadmin_examiner')
	subject=models.ForeignKey(Subject,db_index=True,related_name='examReport_classadmin_genadmin_subject')
	student=models.ForeignKey(	Student,db_index=True,related_name='examReport_classadmin_student_student')
	external_score=models.PositiveSmallIntegerField(blank=True, null=True)
	internal_score=models.PositiveSmallIntegerField()
	final_score=models.PositiveSmallIntegerField()
	remarks=models.TextField()
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='examReport_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="exr"+" "+self.tenant.key+" "+self.student.key+" "+self.exam.key
			self.slug=slugify(item)
		super(Syllabus, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("student","exam","subject","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s' % (self.student, self.exam)

#Homework details.
class Homework(models.Model):
	class_section=models.ForeignKey(class_section,db_index=True,related_name=\
									'Homework_classadmin_eduadmin_classSection')
	subject=models.ForeignKey(Subject,db_index=True,related_name='Homework_classadmin_genadmin_subject')
	homework_details=models.TextField()
	date=models.DateField()
	key=models.CharField(db_index=True,max_length=12)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='Homework_classadmin_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="hw"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_hw_number='001'
			last_hw=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_hw:
				last_hw_number=int(last_hw.key_id[8:])
				next_hw_number='{0:03d}'.format(last_hw_number + 1)
			self.key=data+today_string+next_hw_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(Homework, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s %s' % (self.class_section, self.subject, self.date)