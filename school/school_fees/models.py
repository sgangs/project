import datetime as dt
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import ArrayField

from school_account.models import Account
from school_user.models import Tenant, User
from school_genadmin.models import class_group
from school_eduadmin.models import class_section
from school_student.models import Student 

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)



#This would be the model for yearly fee
class generic_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	month=ArrayField(models.CharField(max_length=3))
	total=models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='genericFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("name","is_active","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


#This would be the line item for each monthly fee.
class generic_fee_list(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=80)
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	generic_fee=models.ForeignKey(generic_fee,db_index=True,related_name='geenricFeeList_yearlyFee')
	account=models.ForeignKey(Account,db_index=True,related_name='geericFeeList_fees_account_account')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='genericFeeList_fees_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("generic_fee","account"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#Late fee calculation model
class late_fee_calculation(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=80, db_index=True)
	last_payment_date=models.PositiveSmallIntegerField(db_index=True)
	year=models.PositiveSmallIntegerField(db_index=True)
	account=models.ForeignKey(Account,db_index=True,related_name='lateFeeCalculation_fees_account_account')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='lateFeeCalculation_fees_user_tenant')
	objects=TenantManager()
	name=models.CharField(max_length=80, default="Late Fee")

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
	# 	unique_together = (("name", "year","tenant",))
	# 	ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#This would be the line item for each late fee.
class late_fee_slab(models.Model):
	id=models.BigAutoField(primary_key=True)
	late_fee=models.ForeignKey(late_fee_calculation,db_index=True,related_name='lateFeeSlab_lateFeeCalculation')
	days_after_due=models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	last_slab=models.BooleanField(db_index=True, default=False)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='lateFeeSlab_fees_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("late_fee","account"))
		# ordering = ('tenant','days_after_due',)
		
	def __str__(self):
		return '%s' % (self.days_after_due)


#Late fee model - register the late fees payed by student
class student_late_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentLateFee_fees_student_student')
	student_class=models.ForeignKey(class_section,db_index=True,related_name='studentLateFee_fees_eduadmin_classSection')
	month=models.PositiveSmallIntegerField(db_index=True)
	year=models.PositiveSmallIntegerField(db_index=True)
# 	# slug=models.SlugField(max_length=56)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentLateFee_fees_user_tenant')
	objects=TenantManager()
	name=models.CharField(max_length=80, default="Late Fee")
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	paid_on=models.DateField()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
	# 	unique_together = (("student","month","year","tenant",))
	# 	ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)



#This model will link class group to monthly and yearly fee for default fee structure.
class group_default_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	classgroup=models.ForeignKey(class_group,db_index=True,related_name='groupDefaultFee_fees_genadmin_classGroup')
	generic_fee=models.ManyToManyField(generic_fee,db_index=True,related_name='groupDefaultFee_genericFee')
	year=models.PositiveSmallIntegerField(db_index=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='groupDefaultFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("classgroup","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#This model will link student to monthly and yearly fee for default fee structure.
class student_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentFee_fees_student_student')
	generic_fee=models.ManyToManyField(generic_fee,db_index=True,related_name='studentFee_genericFee')
	year=models.PositiveSmallIntegerField(db_index=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	
	class Meta:
		unique_together = (("student","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.student)

class student_fee_payment(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentFeePayment_fees_student_student')
	student_class=models.ForeignKey(class_section,db_index=True,related_name='studentFeePayment_fees_eduadmin_classSection')
	month=models.CharField(db_index=True,max_length=3) #This is month for which the fee is paid (Month: Jan, Feb, etc..)
	year=models.PositiveSmallIntegerField(db_index=True) #This is the academic year
	paid_on=models.DateField() #This is the date when the fee is paid_on
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentFeePayment_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("student","month", "year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.student)


class payment_line_item(models.Model):
	id=models.BigAutoField(primary_key=True)
	fee_payment=models.ForeignKey(student_fee_payment,db_index=True,related_name='paymentLineItem_studentFeePayment')
	name=models.CharField(max_length=80)
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='paymentLineItem_fees_user_tenant')
	objects=TenantManager()

	# class Meta:
		# unique_together = (("student","month", "year","tenant",))
		# ordering = ('name',)
		
	