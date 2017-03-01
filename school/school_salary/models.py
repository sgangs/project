from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from school_account.models import Account
from school_hr.models import staff_cadre
from school_teacher.models import Teacher
from school_user.models import Tenant


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)
		

#This is an abstract class for salary lists.
class abstract_salary(models.Model):
	name=models.CharField(max_length=100)
	amount=models.DecimalField(max_digits=8, decimal_places=2)
	
	class Meta:
		abstract = True

class basic_salary_structure(models.Model):
	id=models.BigAutoField(primary_key=True)
	#This is used to calculate the per day cost for calculation due to leaves.
	working_days=models.PositiveSmallIntegerField("Number of working days in month")
	salary_cycle_start=models.PositiveSmallIntegerField()
	salary_cycle_end=models.PositiveSmallIntegerField()
	salary_cycle_payment=models.PositiveSmallIntegerField()
	#employer_statutory_contribution_account FK to Account has to be linked
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='basicSalaryStructure_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
	def __str__(self):
		return '%s' % (self.cadre)




#This would be the model for monthly salary
class monthly_salary(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	# slug=models.SlugField(max_length=50)
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='monthlySalary_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		data="mf"
	# 		tenant=self.tenant.key
	# 		today=dt.date.today()
	# 		today_string=today.strftime('%y%m%d')
	# 		next_mf_number='01'
	# 		last_mf=type(self).objects.filter(tenant=self.tenant).\
	# 					filter(key__contains=today_string).order_by('key').last()
	# 		if last_mf:
	# 			last_mf_number=int(last_mf.key[8:])
	# 			next_mf_number='{0:03d}'.format(last_mf_number + 1)
	# 		self.key=data+today_string+next_mf_number
	# 		toslug=tenant+" "+self.key
	# 		self.slug=slugify(toslug)

	# 	super(monthly_fee, self).save(*args, **kwargs)

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
	def __str__(self):
		return '%s' % (self.name)

class monthly_salary_list(abstract_salary):
	id=models.BigAutoField(primary_key=True)
	monthly_salary=models.ForeignKey(monthly_salary,db_index=True,related_name='monthlySalaryList_monthlySalary')
	account=models.ForeignKey(Account,db_index=True,related_name='monthlySalaryList_salary_account_account')
	display_payslip=models.BooleanField(default=True)
	serial_no=models.PositiveSmallIntegerField(blank=True, null= True)
	affect_pf=models.BooleanField(default=False)
	affect_esi=models.BooleanField(default=False)
	affect_gratuity=models.BooleanField(default=False)
	affect_lop=models.BooleanField(default=False)		#LOP is Loss Of Pay
	is_active=models.BooleanField(default=True)		
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='monthlySalaryList_salary_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
	# 	unique_together = (("monthly_fee","account"))
		ordering = ('display_payslip','serial_no','id')
		
	def __str__(self):
		return '%s' % (self.name)


class yearly_salary(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	month=models.CharField(max_length=3)
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='yearlySalary_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


class yearly_salary_list(abstract_salary):
	id=models.BigAutoField(primary_key=True)
	display_payslip=models.BooleanField(default=True)
	serial_no=models.PositiveSmallIntegerField(blank=True, null= True)
	yearly_salary=models.ForeignKey(yearly_salary,db_index=True,related_name='yearlySalaryList_monthlySalary')
	account=models.ForeignKey(Account,db_index=True,related_name='yearlySalaryList_salary_account_account')
	amount=models.DecimalField(max_digits=7, decimal_places=2)
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='yearlySalaryList_salary_user_tenant')
	objects=TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
	# 	unique_together = (("yearly_fee","account"))
		ordering = ('display_payslip','serial_no','id')
		
	def __str__(self):
		return '%s' % (self.name)

rule_choices=((1,'1'),
	(2,'2'),
	(3,'3'),
	(4,'4'),)

#EE means employee and ER means employer
#Options are EPF, EPS, ESI, EDLI, EPF Admin Charges & EDLI Admin Charges

#Rules are: Rule 1: EPS= Ceiling*Multiplier EPF= Salary*Multiplier
			#Rule 2: EPS= Ceiling*Multiplier EPF= Ceiling*Multiplier
			#Rule 3: EPF= Salary/Ceiling*Multiplier (Ceiling if ceiling is defined)
			#Rule 4: Predefined value

class epf_eps_employer(models.Model):
	id=models.BigAutoField(primary_key=True)
	# statutory_type=models.CharField('Statutory type', max_length=6,choices=statutory_type_choices)
	name=models.TextField(db_index=True,)
	epf_account=models.ForeignKey(Account,db_index=True,related_name='epfEmployer_salary_account_account')
	eps_account=models.ForeignKey(Account,db_index=True,related_name='epsEmployer_salary_account_account')		
	rule=models.PositiveSmallIntegerField('Statutory rule', choices=rule_choices)
	salary_ceiling=models.PositiveIntegerField(blank=True, null=True)
	epf_predefined=models.PositiveIntegerField(blank=True, null=True)
	epf_multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	eps_predefined=models.PositiveIntegerField(blank=True, null=True)
	eps_multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	calculate_epf_admin=models.BooleanField(default=False)
	epf_admin_account=models.ForeignKey(Account,db_index=True,related_name='epfAdmin_salary_account_account', null=True, blank=True)
	epf_admin_multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	epf_admin_minimun=models.PositiveSmallIntegerField(blank=True, null=True)
	epf_admin_predefined=models.PositiveIntegerField(blank=True, null=True)	
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='epfEpsEmployer_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("name","is_active","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#Rules are: Rule 1: ESI= salary/ceiling*multiplier
			#Rule 2: Predefined

class esi_employer(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	esi_account=models.ForeignKey(Account,db_index=True,related_name='esiEmployer_salary_account_account')
	rule=models.PositiveSmallIntegerField('Statutory rule', choices=rule_choices)
	is_active=models.BooleanField(default=True)
	ceiling=models.PositiveIntegerField(blank=True, null=True)
	predefined=models.PositiveIntegerField(blank=True, null=True)
	multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='esiEmployer_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)

#Rules: Rule 1: EPF=Salary*Multiplier
		#Rule 2: EPF=Ceiling*Multiplier
		#Rule 3: EPF=Predefined

class employee_statutory(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	statutory_type=models.CharField(max_length=3) #Options are either EPF or ESI
	account=models.ForeignKey(Account,db_index=True,related_name='employeeStatutory_salary_account_account')
	#Will employer contribution be caped at Rs. 15000? That's why the rule has two options
	rule=models.PositiveSmallIntegerField('Statutory rule', choices=rule_choices)
	is_active=models.BooleanField(default=True)
	ceiling=models.PositiveIntegerField(blank=True, null=True)
	predefined=models.PositiveIntegerField(blank=True, null=True)
	multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='employeeStatutory_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


class edli_employer(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.TextField()
	is_active=models.BooleanField(default=True)
	edli_account=models.ForeignKey(Account,db_index=True,related_name='edliEmployer_salary_account_account')
	edliac_account=models.ForeignKey(Account,db_index=True,related_name='edliacEmployer_salary_account_account')
	rule=models.PositiveSmallIntegerField('Statutory rule', choices=rule_choices)	
	ceiling=models.PositiveIntegerField(blank=True, null=True)
	edli_predefined=models.PositiveIntegerField(blank=True, null=True)
	edli_multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	edliac_min=models.PositiveIntegerField(blank=True, null=True)
	edliac_predefined=models.PositiveIntegerField(blank=True, null=True)
	edliac_multiplier=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='edliEmployer_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# class Meta:
		# unique_together = (("key","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


# class custom_deduction(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	name=models.TextField()
# 	month=models.CharField(max_length=3)
# 	is_active=models.BooleanField(blank=True, null=True)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='customDeduction_salary_user_tenant')
# 	objects=TenantManager()

# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	# class Meta:
# 		# unique_together = (("key","tenant",))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.name)


# class custom_deduction_list(abstract_salary):
# 	id=models.BigAutoField(primary_key=True)
# 	custom_deduction=models.ForeignKey(fixed_deduction,db_index=True,related_name='customDeductionList_customDeduction')
# 	account=models.ForeignKey(Account,db_index=True,related_name='customDeductionList_salary_account_account')
# 	amount=models.DecimalField(max_digits=7, decimal_places=2)
# 	is_active=models.BooleanField(blank=True, null=True)
# 	tenant=models.ForeignKey(Tenant,db_index=True,related_name='customDeductionList_salary_user_tenant')
# 	objects=TenantManager()
	
# 	# def get_absolute_url(self):
# 	# 	return reverse('master:detail', kwargs={'detail':self.slug})

# 	# class Meta:
# 	# 	unique_together = (("yearly_fee","account"))
# 		# ordering = ('name',)
		
# 	def __str__(self):
# 		return '%s' % (self.name)


staff_type=(('Master','Master'),
			('Teacher','Teacher'),
			('Admin','Admin'),
			('Principal','Principal'),
			('Account','Account'),			
			('Collector','Fee Collector'),)


#This model will link class group to monthly and yearly fee for default fee structure.
class cadre_default_salary(models.Model):
	id=models.BigAutoField(primary_key=True)
	cadre=models.ForeignKey(staff_cadre,db_index=True,related_name='cadreDefaultSalary_salary_hr_staffCadre')
	cadre_type=models.CharField(max_length=10, choices=staff_type, db_index=True)
	yearly_salary=models.ManyToManyField(yearly_salary, db_index=True, \
					related_name='cadreDefaultSalary_yearlySalary', blank=True)
	monthly_salary=models.ManyToManyField(monthly_salary,db_index=True,related_name='cadreDefaultSalary_monthlySalary')
	epfEpsEmployer=models.ForeignKey(epf_eps_employer,db_index=True,\
					related_name='cadreDefaultSalary_epfEpsEmployer', blank=True, null=True)
	esiEmployer=models.ForeignKey(esi_employer,db_index=True,related_name='cadreDefaultSalary_esiEmployer', blank=True, null=True)
	edliEmployer=models.ForeignKey(edli_employer,db_index=True,related_name='cadreDefaultSalary_edliEmployer', blank=True, null=True)
	esiEmployee=models.ForeignKey(employee_statutory,db_index=True,related_name='cadreDefaultSalary_esiEmployee',\
					 blank=True, null=True)
	epfEmployee=models.ForeignKey(employee_statutory,db_index=True,related_name='cadreDefaultSalary_epfEmployee',\
					 blank=True, null=True)
	year=models.PositiveSmallIntegerField(db_index=True)
	# slug=models.SlugField(max_length=50)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='cadreDefaultSalary_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+self.classgroup.name+" "+self.monthly_fee.key
	# 		self.slug=slugify(item)

	# 	super(group_default_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("cadre","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.name)


class staff_salary_definition(models.Model):
	id=models.BigAutoField(primary_key=True)
	staff=models.ForeignKey(Teacher,db_index=True,related_name='staffSalary_salary_teacher_teacher')
	staff_type=models.CharField(max_length=10, choices=staff_type, db_index=True)
	yearly_salary=models.ManyToManyField(yearly_salary,db_index=True,related_name='staffSalary_yearlySalary', blank=True)
	monthly_salary=models.ManyToManyField(monthly_salary,db_index=True,related_name='staffSalary_monthlySalary')
	epfEpsEmployer=models.ForeignKey(epf_eps_employer,db_index=True,\
					related_name='staffSalary_epfEpsEmployer', blank=True, null=True)
	esiEmployer=models.ForeignKey(esi_employer,db_index=True,related_name='staffSalary_esiEmployer', blank=True, null=True)
	edliEmployer=models.ForeignKey(edli_employer,db_index=True,related_name='staffSalary_edliEmployer', blank=True, null=True)
	esiEmployee=models.ForeignKey(employee_statutory,db_index=True,related_name='staffSalary_esiEmployee',\
					 blank=True, null=True)
	epfEmployee=models.ForeignKey(employee_statutory,db_index=True,related_name='staffSalary_epfEmployee',\
					 blank=True, null=True)
	year=models.PositiveSmallIntegerField(db_index=True)
	# slug=models.SlugField(max_length=56)
	tenant=models.ForeignKey(Tenant,db_index=True,related_name='staffSalary_salary_user_tenant')
	objects=TenantManager()

	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+self.student.key+" "+self.monthly_fee.key
	# 		self.slug=slugify(item)

	# 	super(student_fee, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("staff","year","tenant",))
		# ordering = ('name',)
		
	def __str__(self):
		return '%s' % (self.staff)


class staff_salary_payment(models.Model):
	id=models.BigAutoField(primary_key=True)
	staff=models.ForeignKey(Teacher,db_index=True,related_name='staffSalaryPayment_salary_teacher_teacher')
	year=models.PositiveSmallIntegerField()
	month=models.CharField(max_length=3)
	gross=models.DecimalField(max_digits=12, decimal_places=2)
	net=models.DecimalField(max_digits=12, decimal_places=2)
	employee_deduction=models.DecimalField(max_digits=12, decimal_places=2)
	employer_contribution=models.DecimalField(max_digits=12, decimal_places=2)
	paid=models.BooleanField(default=False)
	paid_on=models.DateField(null=True, blank=True)
	tenant=models.ForeignKey(Tenant,related_name='staffSalaryPayment_salary_user_tenant')
	objects = TenantManager()
		

	# def get_absolute_url(self):
	# 	return reverse('sales:invoice_detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("staff","month","year","tenant",))
	# 	ordering = ('date',)


	def __str__(self):
		return  '%s %s' % (self.staff, self.total_amount)

		
#This model is for line items of a sales invoice
class salary_payment_list(models.Model):
	salary_payment=models.ForeignKey(staff_salary_payment,related_name='salaryPaymentList_staffSalaryPayment')
	 #The options are monthly, yearly, EPFEE, ESIEE, EPFER, ESIER, EPSER, EPFAC, EDLI, EDLIAC, others
	list_type=models.CharField(max_length=8)
	display_payslip=models.BooleanField(default=True)
	serial_no=models.PositiveSmallIntegerField(blank=True, null= True)
	salary_name=models.TextField()
	account=models.ForeignKey(Account,db_index=True,related_name='salaryPaymentList_salary_account_account')
	amount=models.DecimalField(max_digits=9, decimal_places=2)
	tenant=models.ForeignKey(Tenant,related_name='salaryPaymentList_salary_user_tenant')
	objects = TenantManager()
	