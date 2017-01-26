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

#This is the branch details
# class Branch(models.Model):
# 	name = models.CharField("Name of the branch", max_length=12)
# 	key=models.CharField(db_index=True, max_length=10)
# 	slug=models.SlugField(max_length=35)
# 	address_line_1=models.TextField("Address Line 1",blank=True)
# 	address_line_2=models.TextField("Address Line 2",blank=True)
# 	state=models.CharField(blank=True, max_length=30)
# 	pincode=models.PositiveIntegerField(blank=True)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='branch_genadmin_user_tenant')
# 	objects=TenantManager()
	
# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	def save(self, *args, **kwargs):
# 		if not self.id:
# 			item="br"+" "+self.tenant.key+" "+self.key
# 			self.slug=slugify(item)
# 		super(Product, self).save(*args, **kwargs)

# 	class Meta:
# 		verbose_name_plural = "branches"
# 		unique_together = (("key", "tenant"))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return self.name


#This is the list of subjects to be taught in school.
class Subject(models.Model):
	name=models.CharField("Subject Name", blank=True, max_length=20)
	slug=models.SlugField(max_length=50)
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
		unique_together = (("year", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.year


#This is the class group model. Class has FK to class group and syllabus is assigned to class group
class class_group(models.Model):
	name = models.CharField(db_index=True,max_length=15)
	#branch=models.ForeignKey(Branch,db_index=True,related_name='classGroup_branch')
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
	name=models.CharField(db_index=True,max_length=20)
	class_group=models.ForeignKey(class_group,db_index=True,related_name='batch_classGroup')
	slug=models.SlugField(max_length=45)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='batch_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="ba"+" "+self.tenant.key+" "+self.name
			self.slug=slugify(item)
		super(Batch, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name","tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.name


#This is the house model.
class House(models.Model):
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



# #This is the model for event type. 
# class event_type(models.Model):
# 	name=models.CharField(max_length=20)
# 	#key=models.CharField(db_index=True,max_length=10)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='eventType_genadmin_user_tenant')
# 	objects=TenantManager()
	
# 	class Meta:
# 		unique_together = (("name", "tenant"))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return self.name

event_type=(('E','Exam'),
			('H','Holiday'),
			('O','Other'),)


#This is the list of annual events model.
class annual_calender(models.Model):
	date=models.DateTimeField(db_index=True)
	event=models.CharField(max_length=20)
	event_type=models.CharField('Event type', max_length=1,choices=event_type, default='H')
	#key=models.CharField(db_index=True,max_length=10)
	slug=models.SlugField(db_index=True, max_length=75)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='annualCalender_genadmin_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			toslug=self.tenant.key+" " +self.event+" "+str(self.date)
			self.slug=slugify(toslug)

		super(annual_calender, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("slug", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s:  %s' % (self.event, self.date)
	