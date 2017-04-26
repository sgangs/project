import datetime as dt
from datetime import datetime, timedelta
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_user.models import User, Tenant
from school_teacher.models import Teacher
from school_student.models import Student
from school_genadmin.models import Subject
from school_eduadmin.models import class_section

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

# #This is the library model.
# class Library(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	room=models.CharField("Room name/no.",max_length=15)
# 	slug=models.SlugField(max_length=40)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='library_library_user_tenant')
# 	objects=TenantManager()
	
# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	def save(self, *args, **kwargs):
# 		if not self.id:
# 			item="lib"+" "+self.tenant.key+" "+self.room
# 			self.slug=slugify(item)
# 		super(Library, self).save(*args, **kwargs)

# 	class Meta:
# 		unique_together = (("room", "tenant"))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return self.room


# #This is the librarian model. Each library can have one or multiple librarian
# class Librarian(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	library=models.ForeignKey(Library,db_index=True,related_name='librarian_library')
# 	librarian=models.ForeignKey(Teacher,db_index=True,related_name='librarian_library_teacher_teacher')
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='librarian_library_user_tenant')
# 	objects=TenantManager()
	
# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	# class Meta:
# 	# 	unique_together = (("library","librarian", "tenant"))
# 	# 	ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s %s' % (self.librarian.first_name, self.librarian.last_name,)


#This is the model to store no. of days book can be issued.This is a separate model so that schools can have the option to have  
#different issue period for different student/book
class issue_period(models.Model):
	id=models.BigAutoField(primary_key=True)
	period=models.PositiveSmallIntegerField("No of days book will be issued",default=7)
	# slug=models.SlugField(max_length=30)
	tenant=models.OneToOneField(Tenant, db_index=True,related_name='issuePeriod_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item="isty"+" "+self.tenant.key+" "+str(self.period)
	# 		self.slug=slugify(item)
	# 	super(issue_period, self).save(*args, **kwargs)

	# class Meta:
	# 	unique_together = (("period", "tenant"))
	# 	# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s' % (self.period)

	
#This is the books model.
class Book(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField(db_index=True)
	author=models.CharField(max_length=100,blank=True, null=True)
	publisher=models.CharField(max_length=100,blank=True, null=True)
	publishion_date=models.DateField(blank=True, null=True)
	edition=models.CharField(max_length=40,blank=True, null=True)
	isbn=models.CharField("ISBN",max_length=18,db_index=True,blank=True, null=True)
	remark=models.TextField(blank=True, null=True)
	subject=models.ForeignKey(Subject,db_index=True,null=True, blank=True, related_name='book_library_genadmin_subject')
	# library=models.ForeignKey(Library, related_name='book_library')
	location=models.CharField("Rack location",max_length=30,blank=True, null=True)
	purchased_on=models.DateField(blank=True, null=True)
	price=models.DecimalField(blank=True, null=True, max_digits=7, decimal_places=2)
	school_book_code=models.CharField("School Book ID/Key",max_length=40,blank=True, null=True)
	# book_issued=models.BooleanField()
	quantity=models.PositiveSmallIntegerField(default=1)
	quantity_available=models.PositiveSmallIntegerField(default=1)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='book_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			self.quantity_available=self.quantity
		
		super(Book, self).save(*args, **kwargs)

	def __str__(self):
		return '%s: %s %s' % (self.id, self.name, self.author)

#This is the book issue model.
class book_issue(models.Model):
	id=models.BigAutoField(primary_key=True)
	book=models.ForeignKey(Book, related_name='bookIssue_book')
	issued_on=models.DateField(db_index=True)
	# issued_by=models.ForeignKey(Teacher, related_name='bookIssue_librarian')
	issued_to=models.ForeignKey(Student,db_index=True,related_name='bookIssue_library_student_student')
	# issue_period=models.ForeignKey(issue_period,db_index=True, blank=True, null=True, related_name='bookIssue_issuePeriod')
	issued_class=models.ForeignKey(class_section,db_index=True,related_name='bookIssue_library_eduacmin_classSection')
	remark=models.TextField(blank=True, null=True)
	is_late=models.NullBooleanField(db_index=True)
	returned=models.BooleanField(db_index=True)
	returned_on=models.DateField(null=True, blank=True)
	# return_entry_by=models.ForeignKey(Teacher, related_name='bookReturn_librarian')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='bookIssue_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
	# 	unique_together = (("key", "tenant"))
	# 	ordering = ('name',)
		
	def __str__(self):
		return '%s: %s' % (self.id, self.book.name)


# #This is the book return model.
# class book_return(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	issue_details=models.ForeignKey(book_issue, related_name='bookReturn_bookIssue')
# 	returned_on=models.DateField()
# 	maximum_return_date=models.DateField()
# 	return_entry_by=models.ForeignKey(Librarian, related_name='bookReturn_librarian')
# 	remark=models.TextField(blank=True, null=True)
# 	is_late=models.NullBooleanField()
# 	#return_code=models.CharField(max_length=12)
# 	#slug=models.SlugField(max_length=35)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='bookReturn_library_user_tenant')
# 	objects=TenantManager()
	
# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	def save(self, *args, **kwargs):
# 		if not self.id:
# 			self.maximum_return_date=self.issue_details.issued_on+timedelta(days=self.issue_details.issue_period.period)
# 			if self.returned_on<self.maximum_return_date:
# 				self.is_late=True

# 		super(book_return, self).save(*args, **kwargs)

# 	class Meta:
# 		unique_together=(("issue_details", "tenant"))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s: %s %s %s' % (self.key, self.issue_details.key)