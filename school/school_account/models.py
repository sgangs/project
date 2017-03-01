from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from school_user.models import Tenant


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)
		

#This creates an accounting period
class accounting_period(models.Model):
	id=models.BigAutoField(primary_key=True)
	start=models.DateField(db_index=True,auto_now=False)
	end=models.DateField(db_index=True, auto_now=False)
	#key=models.CharField(db_index=True, max_length=10)
	current_period=models.BooleanField('Current Accounting Period?')
	finalized=models.BooleanField(default=False)
	#slug=models.SlugField(max_length=45)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='accountingPeriod_account_user_tenant')
	objects = TenantManager()
	
	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+str(self.start)+" "+str(self.end)
	# 		self.slug=slugify(item)
	# 	super(accounting_period, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (("start","end", "tenant"))
		ordering = ('start',)

	def __str__(self):
		return '%s-%s' % (self.start.year, self.end.year)
		# return self.start

#This creates an accounting period
# class quarterly_accounting(models.Model):
# 	start=models.DateField(db_index=True,auto_now=False)
# 	end=models.DateField(db_index=True, auto_now=False)
# 	accounting_period=models.ForeignKey(accounting_period,db_index=True, related_name='quarterlyAccounting_accountingPeriod')
# 	finalized=models.NullBooleanField()
# 	slug=models.SlugField(max_length=45)
# 	tenant=models.ForeignKey(Tenant,db_index=True, related_name='quarterlyAccounting_account_user_tenant')
# 	objects = TenantManager()
	
# 	#def get_absolute_url(self):
# 	#	return reverse('master_detail', kwargs={'detail':self.slug})

# 	def save(self, *args, **kwargs):
# 		if not self.id:
# 			item="qa "+self.tenant.key+" "+str(self.start)+" "+str(self.end)
# 			self.slug=slugify(item)
# 		super(accounting_period, self).save(*args, **kwargs)
	
# 	class Meta:
# 		unique_together = (("start","end", "tenant"))
# 		ordering = ('start',)

# 	def __str__(self):
# 		return '%s-%s' % (self.start.year, self.end.year)
# 		# return self.start



#This is a ledger group. here will be a general ledger. User can add ledger groups thereafter.
class ledger_group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=20)
	# slug=models.SlugField(max_length=41)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='ledgergroup_account_user_tenant')
	objects = TenantManager()

	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+self.name
	# 		self.slug=slugify(item)
	# 	super(ledger_group, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name", "tenant"))
		
	def __str__(self):
		return self.name


account_type_general=(('Current Assets','Current Assets'),
				('Long Term Assets','Long Term Assets'),
				('Depreciation','Depreciation'),
				('Current Liabilities','Current Liabilities'),
				('Long Term Liabilities','Long Term Liabilities'),
				# ('Equity','Equity'),
				('Revenue','Revenue'),
				('Fees','Fees'),
				('Indirect Revenue','Indirect Revenue'),
				('Direct Expense','Direct Expense'),
				('Salary','Salary'),
				('Indirect Expense','Indirect Expense'),
				('Equity','Equity'),)

sub_account_type_choices=(('PFEEL','PF Employee - Liability'),
	('PFERL','PF Employer - Liability'),
	('PFERE','PF Employer - Expense'),
	('ESEEL','ESI Employee - Liability'),
	('ESERL','ESI Employer - Liability'),
	('ESERE','ESI Employer - Expense'))


#This is a list of ledgers
class Account(models.Model):
	id=models.BigAutoField(primary_key=True)
	ledger_group=models.ForeignKey(ledger_group, db_index=True, related_name='account_ledgerGroup')
	name=models.CharField(db_index=True, max_length =60)
	remarks=models.TextField(blank=True)
	account_type=models.CharField('Account type', max_length=30,choices=account_type_general)
	sub_account_type=models.CharField('Sub Account type', max_length=5,choices=sub_account_type_choices, blank=True, null=True)
	#opening_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	#opening_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	current_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	current_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	slug=models.SlugField(max_length=40)
	key=models.CharField(db_index=True, max_length=10)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='account_account_user_tenant')
	objects = TenantManager()
	
	def get_absolute_url(self):
		return reverse('accounts:account_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Account, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (("key", "tenant"),("name", "tenant"))
		ordering = ['account_type','name',]

	def __str__(self):
		return self.name

class account_year(models.Model):
	id=models.BigAutoField(primary_key=True)
	account=models.ForeignKey(Account,db_index=True, related_name='accountYear_account')
	opening_debit=models.DecimalField("Opening Debit Balance", max_digits=12, decimal_places=2, default=0)
	opening_credit=models.DecimalField("Opening Credit Balance", max_digits=12, decimal_places=2, default=0)
	closing_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	closing_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	accounting_period=models.ForeignKey(accounting_period,db_index=True, related_name='accountYear_accountingPeriod')
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='accountYear_account_user_tenant')
	objects = TenantManager()

	class Meta:
		unique_together = (("account","accounting_period", "tenant"))


#This is to have each journal as group
class journal_group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=20)
	# slug=models.SlugField(max_length=32)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='journalGroup_account_user_tenant')
	objects = TenantManager()

	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+self.name
	# 		self.slug=slugify(item)
	# 	super(journal_group, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("name", "tenant"))
		
	def __str__(self):
		return self.name

#This is a list of journal entry
class Journal(models.Model):
	id=models.BigAutoField(primary_key=True)
	date=models.DateTimeField(default=datetime.now)
	group=models.ForeignKey(journal_group,related_name='journal_journalGroup')
	remarks=models.CharField(max_length=80, blank=True, null=True)
	slug=models.SlugField(max_length=50)
	key=models.CharField(db_index=True, max_length=20)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='journal_account_user_tenant')
	objects = TenantManager()

	def get_absolute_url(self):
		return reverse('accounts:journal_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			data="jr"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			to_filter="jr"+today_string
			next_journal_number='001'
			last_journal=type(self).objects.filter(tenant=self.tenant).\
							filter(key__contains=to_filter).order_by('key').last()
			if last_journal:
				last_journal_number=int(last_journal.key[8:])
				next_journal_number='{0:03d}'.format(last_journal_number + 1)
			self.key=data + today_string + next_journal_number
			toslug=self.tenant.key+" "+self.key
			self.slug=slugify(toslug)
		super(Journal, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (("key", "tenant"))
		ordering = ('date','group',)

	def __str__(self):
		return str(self.date)

#This is to link to journal entry line items
class journal_entry(models.Model):
	id=models.BigAutoField(primary_key=True)
	transaction_type=(('Credit','Credit'),
				('Debit','Debit'))	
	journal=models.ForeignKey(Journal,db_index=True, related_name='journalEntry_journal')
	account=models.ForeignKey(Account,related_name='journalEntry_account')
	transaction_type=models.CharField('Transaction type', max_length=6,choices=transaction_type)
	value=models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='journalEntry_account_user_tenant')
	objects = TenantManager()
	
	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	#def save(self, *args, **kwargs):
	#	if not self.id:
	#		item=self.tenant.key+" "+self.key
	#		self.slug=slugify(item)
	#	super(Account, self).save(*args, **kwargs)
	
	class Meta:
		unique_together = (("journal", "account"))
		ordering = ('journal','-transaction_type',)

	def __str__(self):
		return self.account.name


#This model is for modes of payment
class payment_mode(models.Model):
	id=models.BigAutoField(primary_key=True)
	name = models.CharField('Payment Mode Name', db_index=True, max_length=20)
	payment_account=models.ForeignKey(Account,related_name='paymentMode_account')
	default=models.BooleanField('Default Payment Mode ?', default=False)
	# slug=models.SlugField(max_length=32)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='paymentMode_account_user_tenant')
	objects = TenantManager()

	# def save(self, *args, **kwargs):
	# 	if not self.id:
	# 		item=self.tenant.key+" "+self.name
	# 		self.slug=slugify(item)
	# 	super(payment_mode, self).save(*args, **kwargs)

	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("payment_account", "name", "tenant"))
		
	def __str__(self):
		return self.name