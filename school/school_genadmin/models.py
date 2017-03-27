import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import Tenant


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


#This is the list of subjects to be taught in school.
class Subject(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField("Subject Name", blank=True, max_length=20)
	# slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='subject_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="sub"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		super(Subject, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name


class academic_year(models.Model):
	id=models.BigAutoField(primary_key=True)
	year=models.PositiveSmallIntegerField("Academic Year: If year is 2016-17, enter 2016")
	start=models.DateField()
	end=models.DateField()
	slug=models.SlugField(max_length=50)
	current_academic_year=models.BooleanField()
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='academicYear_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="aca"+" "+self.tenant.key+" "+str(self.year)
			self.slug=slugify(item)
		super(academic_year, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("year", "tenant"),("start", "tenant"),("end", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.year


standard_choices=((-6,'Lower Nusrsery'),
		(-5,'Nursery'),
		(-4,'Upper Nursery'),
		(-3,'Lower KG'),
		(-2,'Kindergarten'),
		(-1,'Upper KG'),
		(1,'One'),
		(2,'Two'),
		(3,'Three'),
		(4,'Foure'),
		(5,'Five'),
		(6,'Six'),
		(7,'Seven'),
		(8,'Eight'),
		(9,'Nine'),
		(10,'Ten'),
		(11,'Eleven'),
		(12,'Twelve'))

#This is the class group model. Class has FK to class group and syllabus is assigned to class group
class class_group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name = models.CharField(db_index=True,max_length=15)
	standard=models.IntegerField(db_index=True, choices=standard_choices)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='classGroup_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="cl"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		super(class_group, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name","tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name


class Batch(models.Model):
	id=models.BigAutoField(primary_key=True)
	start_year=models.PositiveSmallIntegerField("Batch Starting Year")
	end_year=models.PositiveSmallIntegerField("Batch Ending Year")
	name=models.CharField(db_index=True,max_length=9)
	slug=models.SlugField(max_length=45)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='batch_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="ba"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		self.name=str(self.start_year)+"-"+str(self.end_year)
		super(Batch, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name","tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name


#This is the house model.
class House(models.Model):
	id=models.BigAutoField(primary_key=True)
	name = models.CharField(db_index=True,max_length=20)
	house_motto = models.TextField(blank=True)
	#branch=models.ForeignKey(Branch,db_index=True,related_name='house_branch')
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='house_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="ho"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		super(House, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name



event_type=((1,'Holiday'),
			(2,'Exam'),
			(3,'Exception'),
			(4,'Others'))

attendance_type=((1,'Working Day'),
			(2,'Non working day'),)


#This is the list of annual events model.
class annual_calender(models.Model):
	id=models.BigAutoField(primary_key=True)
	date=models.DateTimeField(db_index=True)
	event=models.CharField(max_length=20)
	event_type=models.PositiveSmallIntegerField('Event type', choices=event_type, default='1')
	attendance_type=models.PositiveSmallIntegerField('Attendance type', choices=attendance_type, default='2')
	#key=models.CharField(db_index=True,max_length=10)
	# slug=models.SlugField(db_index=True, max_length=75)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='annualCalender_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		ordering = ('date',)

#Annual Calendar Holiday Rules
class annual_holiday_rules(models.Model):
	id=models.BigAutoField(primary_key=True)
	title=models.CharField(max_length=25)
	week=models.PositiveSmallIntegerField()
	day=models.PositiveSmallIntegerField(db_index=True, default=5)
	slug=models.SlugField(max_length=80)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='annualHolidayRules_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			toslug=self.tenant.key+" " +self.title
			self.slug=slugify(toslug)
		super(annual_holiday_rules, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("slug", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.ttile)

#Notice Board. How to run a cron to auto delete these after show_until?
class notice_board(models.Model):
	id=models.BigAutoField(primary_key=True)
	title=models.CharField(max_length=100)
	details=models.TextField()
	show_from=models.DateField("Date")
	show_until=models.DateField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='noticeBoard_eduadmin_user_tenant')
	objects=TenantManager()

	class Meta:
		# unique_together = (("day","period","year", "tenant"))
		ordering = ('show_from','show_until')
		
	def __str__(self):
		return '%s ' % (self.title)

# class gate_pass(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	visitor_name=models.CharField(max_length=50)
# 	visit_purpose=models.TextField()
# 	date=models.DateField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='noticeBoard_eduadmin_user_tenant')
# 	objects=TenantManager()


# This is for multiple services

# class maintainance_type(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	maintainance_type=models.TextField()
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='maintainanceType_genadmin_user_tenant')
# 	objects=TenantManager()
	
# 	class Meta:
# 		unique_together = (("maintainance_type", "tenant"))
		
# 	def __str__(self):
# 		return self.name

# class maintainance_detail(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	detail=models.TextField()
# 	date=models.DateField() #Date of maintainance
# 	# maintainance_by= #We need to check who will do the maintainance
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='maintainanceDetail_genadmin_user_tenant')
# 	objects=TenantManager()
	
# 	class Meta:
# 		unique_together = (("maintainance_type", "tenant"))
		
# 	def __str__(self):
# 		return self.name