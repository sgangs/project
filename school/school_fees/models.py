import datetime as dt
from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from school_account.models import Account
from school_user.models import Tenant, User
from school_genadmin.models import class_group
from school_eduadmin.models import class_section
from school_student.models import Student 




class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


#This is an abstract class for fee lists.
class abstract_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(max_length=100)
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	
	class Meta:
		abstract = True



#This would be the model for monthly fee
class monthly_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	#subject=models.ForeignKey(Subject,db_index=True,related_name='Homework_classadmin_genadmin_subject')
	name=models.TextField()
	key=models.CharField(db_index=True,max_length=12)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='monthlyFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="mf"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_mf_number='01'
			last_mf=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_mf:
				last_mf_number=int(last_mf.key[8:])
				next_mf_number='{0:03d}'.format(last_mf_number + 1)
			self.key=data+today_string+next_mf_number
			toslug=tenant+" "+self.key
			self.slug=slugify(toslug)

		super(monthly_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key","tenant",))
		# ordering = ('name',)
	def __str__(self):
		return '%s' % (self.name)

#This would be the line item for each monthly fee.
class monthly_fee_list(abstract_fee):
	id=models.BigAutoField(primary_key=True)
	monthly_fee=models.ForeignKey(monthly_fee,db_index=True,related_name='monthlyFeeList_monthlyFee')
	account=models.ForeignKey(Account,db_index=True,related_name='monthlyFeeList_fees_account_account')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='monthlyFeeList_fees_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("monthly_fee","account"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


#This would be the model for yearly fee
class yearly_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	#subject=models.ForeignKey(Subject,db_index=True,related_name='Homework_classadmin_genadmin_subject')
	name=models.TextField()
	month=models.CharField(max_length=3)
	key=models.CharField(db_index=True,max_length=12)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='yearlyFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="yf"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_yf_number='01'
			last_yf=type(self).objects.filter(tenant=self.tenant).\
						filter(key__contains=today_string).order_by('key').last()
			if last_yf:
				last_yf_number=int(last_yf.key[8:])
				next_yf_number='{0:03d}'.format(last_yf_number + 1)
			self.key=data+today_string+next_yf_number
			toslug=tenant+" " +self.key
			self.slug=slugify(toslug)

		super(yearly_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


#This would be the line item for each monthly fee.
class yearly_fee_list(abstract_fee):
	id=models.BigAutoField(primary_key=True)
	yearly_fee=models.ForeignKey(yearly_fee,db_index=True,related_name='yearlyFeeList_monthlyFee')
	account=models.ForeignKey(Account,db_index=True,related_name='yearlyFeeList_fees_account_account')
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='yearlyFeeList_fees_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("yearly_fee","account"))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


#This model will link class group to monthly and yearly fee for default fee structure.
class group_default_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	classgroup=models.ForeignKey(class_group,db_index=True,related_name='groupDefaultFee_fees_genadmin_classGroup')
	yearly_fee=models.ManyToManyField(yearly_fee,db_index=True,related_name='groupDefaultFee_yearlyFee')
	monthly_fee=models.ForeignKey(monthly_fee,db_index=True,related_name='groupDefaultFee_monthlyFee')
	#fee_structure=models.ManyToManyField(fee_structure,db_index=True,related_name='groupDefaultFee_feeStructure')
	year=models.PositiveSmallIntegerField(db_index=True)
	slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='groupDefaultFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.classgroup.name+" "+self.monthly_fee.key
			self.slug=slugify(item)

		super(group_default_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("classgroup","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#This model will link student to monthly and yearly fee for default fee structure.
class student_fee(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentFee_fees_student_student')
	#fee_structure=models.ManyToManyField(fee_structure,db_index=True,related_name='studentFee_feeStructure')
	yearly_fee=models.ManyToManyField(yearly_fee,db_index=True,related_name='studentFee_yearlyFee')
	monthly_fee=models.ForeignKey(monthly_fee,db_index=True,related_name='studentFee_monthlyFee')
	year=models.PositiveSmallIntegerField(db_index=True)
	slug=models.SlugField(max_length=56)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentFee_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.student.key+" "+self.monthly_fee.key
			self.slug=slugify(item)

		super(student_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("student","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.student)

class student_fee_payment(models.Model):
	id=models.BigAutoField(primary_key=True)
	student=models.ForeignKey(Student,db_index=True,related_name='studentFeePayment_fees_student_student')
	student_class=models.ForeignKey(class_section,db_index=True,related_name='studentFeePayment_fees_eduadmin_classSection')
	month=models.CharField(db_index=True,max_length=3)
	year=models.PositiveSmallIntegerField(db_index=True)
	paid_on=models.DateField()
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	slug=models.SlugField(max_length=56)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentFeePayment_fees_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.student.key+" "+str(self.year)+" "+self.month
			self.slug=slugify(item)

		super(student_fee_payment, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("student","month", "year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.student)

# #Late fee model
# class student_late_fee(models.Model):
# 	student=models.ForeignKey(Student,db_index=True,related_name='studentLateFee_fees_student_student')
# 	month=models.PositiveSmallIntegerField(db_index=True)
# 	year=models.PositiveSmallIntegerField(db_index=True)
# 	# slug=models.SlugField(max_length=56)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='studentLateFee_fees_user_tenant')
# 	objects=TenantManager()

# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	# def save(self, *args, **kwargs):
# 	# 	if not self.id:
# 	# 		item=self.tenant.key+" "+self.student.key+" "+self.monthly_fee.key
# 	# 		self.slug=slugify(item)

# 		# super(student_fee, self).save(*args, **kwargs)

# 	# class Meta:
# 	# 	unique_together = (("student","month","year","tenant",))
# 	# 	ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.name)