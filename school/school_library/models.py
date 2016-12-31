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

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the library model.
class Library(models.Model):
	room=models.CharField("Room name/no.",max_length=15)
	slug=models.SlugField(max_length=40)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='library_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="lib"+" "+self.tenant.key+" "+self.room
			self.slug=slugify(item)
		super(Library, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("room", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return self.room


#This is the librarian model. Each library can have one or multiple librarian
class Librarian(models.Model):
	library=models.ForeignKey(Library,db_index=True,related_name='librarian_library')
	librarian=models.ForeignKey(Teacher,db_index=True,related_name='librarian_library_teacher_teacher')
	slug=models.SlugField(max_length=55)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='librarian_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="lbr"+" "+self.tenant.key+" "+ " "+self.library.name+" "+self.librarian.key
			self.slug=slugify(item)
		super(Library, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("library","librarian", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s' % (self.librarian.key, self.librarian.first_name, self.librarian.last_name,)


#This is the model to store no. of days book can be issued.This is a separate model so that schools can have the option to have  
#different issue period for different student/book
class issue_period(models.Model):
	period=models.PositiveSmallIntegerField("No of days book will be issued",default=7)
	slug=models.SlugField(max_length=30)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='issuePeriod_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item="isty"+" "+self.tenant.key+" "+str(self.period)
			self.slug=slugify(item)
		super(Library, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("period", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s' % (self.key, self.name, self.author)

	
#This is the books model.
class Book(models.Model):
	name=models.TextField(db_index=True)
	author=models.TextField(db_index=True,blank=True, null=True)
	publisher=models.TextField(blank=True, null=True)
	edition=models.CharField(max_length=40,blank=True, null=True)
	isbn=models.CharField(max_length=18,db_index=True,blank=True, null=True)
	remark=models.TextField(blank=True, null=True)
	subject=models.ForeignKey(Subject,db_index=True,related_name='book_library_genadmin_subject')
	library=models.ForeignKey(Library, related_name='book_library')
	location=models.CharField("Rack location",max_length=30,blank=True, null=True)
	purchased_on=models.DateField()
	price=models.DecimalField(max_digits=7, decimal_places=2)
	school_book_code=models.CharField("Internal Book Code",max_length=40,blank=True, null=True)
	key=models.CharField(max_length=12)
	slug=models.SlugField(max_length=35)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='book_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="bk"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_book_number='0001'
			last_book=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_book:
				last_book_number=int(last_book.key_id[8:])
				next_book_number='{0:04d}'.format(last_book_number + 1)
			self.key=data+today_string+next_book_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(Book, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s' % (self.key, self.name, self.author)

#This is the book issue model.
class book_issue(models.Model):
	book=models.ForeignKey(Book, related_name='bookIssue_book')
	issued_on=models.DateField()
	issued_by=models.ForeignKey(Librarian, related_name='bookIssue_librarian')
	issued_to=models.ForeignKey(Student,db_index=True,related_name='bookIssue_library_student_student')
	issue_period=models.ForeignKey(issue_period,db_index=True,related_name='bookIssue_issuePeriod')
	remark=models.TextField(blank=True, null=True)
	#issue_code=models.CharField(max_length=12)
	key=models.CharField(max_length=12)
	returned=models.BooleanField()
	slug=models.SlugField(max_length=35)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='bookIssue_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="bi"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_issue_number='0001'
			last_issue=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_issue:
				last_issue_number=int(last_book.key_id[8:])
				next_issue_number='{0:04d}'.format(last_issue_number + 1)
			self.key=data+today_string+next_issue_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(book_issue, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s %s' % (self.key, self.book.name, self.issued_to.first_name, self.issued_to.last_name)


#This is the book return model.
class book_return(models.Model):
	issue_details=models.ForeignKey(book_issue, related_name='bookReturn_bookIssue')
	returned_on=models.DateField()
	maximum_return_date=models.DateField()
	return_entry_by=models.ForeignKey(Librarian, related_name='bookReturn_librarian')
	remark=models.TextField(blank=True, null=True)
	is_late=models.BooleanField
	#return_code=models.CharField(max_length=12)
	#slug=models.SlugField(max_length=35)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='bookReturn_library_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			self.maximum_return_date=self.issue_details.issued_on+timedelta(days=self.issue_details.issue_period.period)
			if self.returned_on<self.maximum_return_date:
				self.is_late=True

		super(book_return, self).save(*args, **kwargs)

	class Meta:
		unique_together=(("issue_details", "tenant"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s: %s %s %s' % (self.key, self.issue_details.key)