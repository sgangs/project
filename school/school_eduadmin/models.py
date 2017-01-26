import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import User, Tenant
from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import class_group, Subject, House

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the class model. Each student has a class.
class class_section(models.Model):
	name = models.CharField("Class Name with section", db_index=True,blank=True, max_length=15)
	room = models.CharField("Room name/no.",blank=True, max_length=15)
	classgroup=models.ForeignKey(class_group,db_index=True,related_name='classSection_classadmin_classGroup_genadmin')
	slug=models.SlugField(max_length=40)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='classsection_classadmin_user_tenant')
	objects=TenantManager()
	
	def get_absolute_url(self):
		return reverse('eduadmin:class_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="cs"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		super(class_section, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name

class classteacher(models.Model):
	class_section=models.ForeignKey(class_section,db_index=True,related_name='classteacher_classSection')
	class_teacher=models.ForeignKey(Teacher,db_index=True,related_name='classteacher_eduadmin_teacher_teacher')
	year=models.PositiveSmallIntegerField(db_index=True,default=datetime.now().year)
	slug=models.SlugField(max_length=42)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='classteacher_eduadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="clt"+" "+self.tenant.key+" "+self.class_section.name+" "+str(self.year)
			self.slug=slugify(item)
		super(classteacher, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("class_section", "year","tenant"))
		#ordering = ('name',)
		
	def __str__(self):
		return '%s %s %s' % (self.class_section, self.class_teacher, self.year)

class classstudent(models.Model):
	class_section=models.ForeignKey(class_section,db_index=True,related_name='classstudent_classSection')
	roll_no=models.CharField(max_length=10)
	student=models.ForeignKey(Student,db_index=True,related_name='classstudent_eduadmin_student_student')
	year=models.PositiveSmallIntegerField(db_index=True,default=datetime.now().year)
	slug=models.SlugField(max_length=40)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='classstudent_eduadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="cls"+" "+self.tenant.key+" "+self.student.key+" "+str(self.year)
			self.slug=slugify(item)
		super(classstudent, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("class_section","student","year", "tenant"), ("class_section", "roll_no","year", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s - %s' % (self.class_section, self.student, self.year)



#This is for the syllabus class group wise. 
class Syllabus(models.Model):
	class_group=models.ForeignKey(class_group,db_index=True,related_name='syllabus_eduadmin_classGroup_genadmin')
	subject=models.ForeignKey(Subject,db_index=True,related_name='syllabus_eduadmin_subject_genadmin')
	key=models.CharField(db_index=True, max_length=40)
	topics=models.TextField()
	year=models.PositiveSmallIntegerField(db_index=True,default=datetime.now().year)
	slug=models.SlugField(max_length=65)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='syllabus_eduadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			self.key=self.class_group.name+self.subject.name+str(self.year)
			item="syl"+" "+self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Syllabus, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.key

class Exam(models.Model):
	name=models.CharField(db_index=True,max_length=15)
	key=models.CharField(db_index=True,max_length=20)
	total=models.PositiveSmallIntegerField()
	year=models.PositiveSmallIntegerField(db_index=True,default=datetime.now().year)
	slug=models.SlugField(max_length=45)
	external_examiner=models.BooleanField("Will threre be external examiners to check student copies?", default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='exam_classadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			self.key=self.name+" "+str(self.year)
			item="exm"+" "+self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Exam, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)		

	def __str__(self):
		return '%s %s' % (self.name, self.year)

#This is for subject teacher for each subject. Lets create a FK to syllabus, so as to ease in rendering views.
class subject_teacher(models.Model):
	subject=models.ForeignKey(Subject,db_index=True,related_name='subjectTeacher_eduadmin_subject_genadmin')
	class_section=models.ForeignKey(class_section,db_index=True,related_name='subjectTeacher_classSection')
	teacher=models.ForeignKey(Teacher,db_index=True,related_name='subjectTeacher_eduadmin_teacher_teacher')
	year=models.PositiveSmallIntegerField(db_index=True,default=datetime.now().year)
	key=models.CharField(db_index=True,max_length=60)
	slug=models.SlugField(max_length=85)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='subjectTeacher_eduadmin_user_tenant')
	objects=TenantManager()
	
	def save(self, *args, **kwargs):
		if not self.id:
			self.key=self.class_section.name+" "+self.subject.name+" "+self.teacher.key+" "+str(self.year)
			item="suj"+" "+self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(subject_teacher, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))

	def __str__(self):
		return '%s %s %s' % (self.class_section.name, self.subject.name, self.teacher.key)

#This is for storing internal and external examiner for each exam
class Examiner(models.Model):
	class_section=models.ForeignKey(class_section,db_index=True,related_name=\
									'Examiner_eduadmin_eduadmin_classSection')
	exam=models.ForeignKey(Exam,db_index=True,related_name='Examiner_exam')
	subject = models.ForeignKey(Subject,db_index=True,related_name='Examiner_eduadmin_genadmin_subject')
	external_examiner=models.ForeignKey(Teacher,db_index=True,blank=True, null=True,\
					related_name='ExaminerExternal_eduadmin_teacher_teacher')
	internal_examiner=models.ForeignKey(Teacher,db_index=True,\
					related_name='ExaminerInternal_eduadmin_teacher_teacher')
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='Examiner_eduadmin_user_tenant')
	objects=TenantManager()

	def save(self, *args, **kwargs):
		if not self.id:
			item="ein"+" "+self.tenant.key+" "+self.exam.key+" "+self.class_section.name+" "+self.subject.name
			self.slug=slugify(item)
		super(Syllabus, self).save(*args, **kwargs)
	class Meta:
		unique_together = (("exam","class_section","subject", "tenant"))
	def __str__(self):
		return '%s %s %s' % (self.class_section.name, self.subject.name, self.teacher.key)

class student_house(models.Model):
	house=models.ForeignKey(House,db_index=True,related_name='studentHouse_eduadmin_genadmin_house')
	student=models.ForeignKey(Student,db_index=True,related_name='studentHouse_eduadmin_student_student')
	year=models.PositiveSmallIntegerField(default=datetime.now().year)
	slug=models.SlugField(max_length=65)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentHouse_eduadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="sho"+""+self.tenant.key+" "+self.student.key+" "+self.house.name+" "+self.year
			self.slug=slugify(item)
		super(classstudent, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("house","student","year", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s %s' % (self.house, self.student, self.year)

class total_period(models.Model):
	number_period=models.PositiveSmallIntegerField("Number of Periods in a day",db_index=True)
	tenant=models.OneToOneField(Tenant, db_index=True,related_name='totalPeriod_eduadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	#class Meta:
		#unique_together = ("tenant")
		# ordering = ('name',)
		
	def __str__(self):
		return self.number_periods

class period(models.Model):
	day=models.CharField(max_length=9)
	period=models.PositiveSmallIntegerField()
	year=models.PositiveSmallIntegerField()
	slug=models.SlugField(max_length=42)
	class_section=models.ForeignKey(class_section,db_index=True,related_name='period_classSection')
	subject=models.ForeignKey(Subject,db_index=True, related_name='period_eduadmin_subject_genadmin')
	teacher=models.ForeignKey(Teacher,db_index=True, related_name='period_eduadmin_teacher_teacher')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='period_eduadmin_user_tenant')
	objects=TenantManager()

	def save(self, *args, **kwargs):
		if not self.id:
			item="pe"+""+self.tenant.key+" "+self.day+" "+self.period+" "+self.year
			self.slug=slugify(item)
		super(period, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("day","period","year", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s %s %s' % (self.day, self.period)