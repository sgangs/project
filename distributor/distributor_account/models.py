from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from datetime import datetime

from distributor_user.models import Tenant
from distributor.variable_list import account_type_general
from distributor_master.models import Product
from distributor.variable_list import state_list, account_relation_list


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)
		

#This creates an accounting period
class accounting_period(models.Model):
	id=models.BigAutoField(primary_key=True)
	start=models.DateField(db_index=True,auto_now=False)
	end=models.DateField(db_index=True, auto_now=False)
	current_period=models.BooleanField('Current Accounting Period?')
	finalized=models.BooleanField(default=False)
	is_first_year=models.BooleanField(default=False)
	tenant=models.ForeignKey(Tenant, related_name='accountingPeriod_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)	
	
	class Meta:
		unique_together = (("start","end", "tenant"))
		ordering = ('start',)

	def __str__(self):
		return '%s-%s' % (self.start.year, self.end.year)
		# return self.start

#This is a ledger group. here will be a general ledger. User can add ledger groups thereafter.
class ledger_group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=20)
	tenant=models.ForeignKey(Tenant, related_name='ledgergroup_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("name", "tenant"))
		
	def __str__(self):
		return self.name


# #This is a ledger group. here will be a general ledger. User can add ledger groups thereafter.
# class accounting_group(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	name=models.CharField(max_length=20)
# 	tenant=models.ForeignKey(Tenant, related_name='accountingGroup_account_user_tenant')
# 	objects = TenantManager()
# 	updated = models.DateTimeField(auto_now=True)

# 	class Meta:
# 		unique_together = (("name", "tenant"))
		
# 	def __str__(self):
# 		return self.name



#This is a list of ledgers
class Account(models.Model):
	id=models.BigAutoField(primary_key=True)
	ledger_group=models.ForeignKey(ledger_group, related_name='account_ledgerGroup', blank=True, null=True)
	# accounting_group=models.ForeignKey(accounting_group, related_name='account_accountingGroup', blank=True, null=True)
	name=models.CharField(db_index=True, max_length =60)
	remarks=models.TextField(blank=True, null=True)
	account_type=models.CharField('Account type', max_length=30,choices=account_type_general)
	key=models.CharField(db_index=True, max_length=15)
	is_contra=models.BooleanField(default=False)
	tenant=models.ForeignKey(Tenant, related_name='account_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	
	class Meta:
		unique_together = (("key", "tenant"),("name", "tenant"))
	
	def __str__(self):
		return self.name

class account_relation(models.Model):
	id=models.BigAutoField(primary_key=True)
	account = models.ForeignKey(Account, related_name='accountRelation_account')
	relation=models.PositiveSmallIntegerField(db_index=True, choices=account_relation_list)
	tenant=models.ForeignKey(Tenant, related_name='accountRelation_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	
	class Meta:
		unique_together = (("relation", "tenant"))
	
	def __str__(self):
		return self.relation


class account_year(models.Model):
	id=models.BigAutoField(primary_key=True)
	account=models.ForeignKey(Account,db_index=True, related_name='accountYear_account')
	is_first_year=models.BooleanField(default=True)
	opening_debit=models.DecimalField("Opening Debit Balance", max_digits=12, decimal_places=2, default=0)
	opening_credit=models.DecimalField("Opening Credit Balance", max_digits=12, decimal_places=2, default=0)
	first_debit=models.DecimalField("Debit Balance as on date of registration", max_digits=12, decimal_places=2,\
									blank=True, null=True)
	first_credit=models.DecimalField("Credit Balance as on date of registration", max_digits=12, decimal_places=2,\
									blank=True, null=True)	
	current_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	current_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)	
	closing_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	closing_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	accounting_period=models.ForeignKey(accounting_period, related_name='accountYear_accountingPeriod')
	tenant=models.ForeignKey(Tenant, related_name='accountYear_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("account","accounting_period", "tenant"))


class account_inventory(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length =60)
	key=models.CharField(max_length=15)
	tenant=models.ForeignKey(Tenant, related_name='accountInventory_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	
	class Meta:
		unique_together = (("key", "tenant"),("name", "tenant"))
		# ordering = ['account_type','name',]

	def __str__(self):
		return self.name

class account_year_inventory(models.Model):
	id=models.BigAutoField(primary_key=True)
	account_inventory=models.ForeignKey(account_inventory, related_name='accountYearInventory_accountInventory')
	opening_debit=models.DecimalField("Opening Debit Balance", max_digits=12, decimal_places=2, default=0)
	opening_credit=models.DecimalField("Opening Credit Balance", max_digits=12, decimal_places=2, default=0)
	first_debit=models.DecimalField("Debit Balance as on date of registration", max_digits=12, decimal_places=2,\
									blank=True, null=True)
	first_credit=models.DecimalField("Credit Balance as on date of registration", max_digits=12, decimal_places=2,\
									blank=True, null=True)	
	current_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	current_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)	
	closing_debit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	closing_credit=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	accounting_period=models.ForeignKey(accounting_period, related_name='accountYearInventory_accountingPeriod')
	is_first_year=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant, related_name='accountYearInventory_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("account_inventory","accounting_period", "tenant"))


#This is to have each journal as group
class journal_group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=20)
	# slug=models.SlugField(max_length=32)
	tenant=models.ForeignKey(Tenant, related_name='journalGroup_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("name", "tenant"))
		
	def __str__(self):
		return self.name

#transaction options are:
#1 - Purchase
#2 - Purchase Payment
#3 - Purchase Debit Note/Purchase Return
#4 - Sales
#5 - Sales Collection
#6 - Sales Credit Note
#7 - Retail Sales
#8 - Retail Credit Note
#9 - Normal Journal Entry
#10 - Service Sales
#11 - Service Credit Note
#12 - Opening Payment Vendor
#13 - Other Payment Vendor
#14 - Opening Payment Customer
#15 - Other Payment Customer

#This is a list of journal entry
class Journal(models.Model):
	id=models.BigAutoField(primary_key=True)
	date=models.DateField(default=datetime.now)
	group=models.ForeignKey(journal_group,related_name='journal_journalGroup')
	remarks=models.CharField(max_length=140, blank=True, null=True)
	transaction_bill_id=models.BigIntegerField(db_index=True, blank=True, null=True)
	trn_type=models.PositiveSmallIntegerField(db_index=True,blank=True, null=True)
	other_data = JSONField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,db_index=True, related_name='journal_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	# def get_absolute_url(self):
	# 	return reverse('accounts:journal_detail', kwargs={'detail':self.slug})

	# class Meta:
	# 	unique_together = (("key", "tenant"))
	# 	ordering = ('date','group',)

	def __str__(self):
		return str(self.date)

#This is to link to journal entry line items
class journal_entry(models.Model):
	id=models.BigAutoField(primary_key=True)
	transaction_type=((1,'Debit'),
		(2,'Credit'),)
	activity_type=models.PositiveSmallIntegerField('Activity Type', blank=True, null=True) #For cash flow
	journal=models.ForeignKey(Journal, related_name='journalEntry_journal')
	account=models.ForeignKey(Account,related_name='journalEntry_account')
	transaction_type=models.PositiveSmallIntegerField('Transaction type', choices=transaction_type)
	value=models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	related_data = JSONField(blank=True, null=True) #must contain just customer_id/vendor_id . Can add other data as customer name later.
	tenant=models.ForeignKey(Tenant, related_name='journalEntry_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	class Meta:
		# unique_together = (("journal", "account"))
		ordering = ('journal','-transaction_type',)

	def __str__(self):
		return self.account.name


#transaction options are:
#1 - Purchase
#2 - Purchase Payment
#3 - Purchase Debit Note
#4 - Sales
#5 - Sales Collection
#6 - Sales Credit Note
#7 - Retail Sales
#8 - Retail Credit Note

class journal_inventory(models.Model):
	id=models.BigAutoField(primary_key=True)
	date=models.DateField(default=datetime.now)
	transaction_bill_id=models.BigIntegerField(db_index=True, blank=True, null=True)
	trn_type=models.PositiveSmallIntegerField(db_index=True,blank=True, null=True)
	tenant=models.ForeignKey(Tenant, related_name='journalInventory_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	# def get_absolute_url(self):
	# 	return reverse('accounts:journal_detail', kwargs={'detail':self.slug})

	# class Meta:
	# 	unique_together = (("key", "tenant"))
	# 	ordering = ('date','group',)

	def __str__(self):
		return str(self.date)

#This is to link to journal entry line items
class journal_entry_inventory(models.Model):
	id=models.BigAutoField(primary_key=True)
	transaction_type=((1,'Debit'),
		(2,'Credit'),)
	journal=models.ForeignKey(journal_inventory, related_name='journalEntryInventory_journalInventory')
	account=models.ForeignKey(account_inventory,related_name='journalEntryInventory_accountInventory')
	transaction_type=models.PositiveSmallIntegerField('Transaction type', choices=transaction_type)
	value=models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
	tenant=models.ForeignKey(Tenant, related_name='journalEntryInventory_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	#def get_absolute_url(self):
	#	return reverse('master_detail', kwargs={'detail':self.slug})

	class Meta:
		# unique_together = (("journal", "account"))
		ordering = ('journal','-transaction_type',)

	def __str__(self):
		return self.account.name



#This model is for modes of payment
class payment_mode(models.Model):
	id=models.BigAutoField(primary_key=True)
	name = models.CharField('Payment Mode Name', db_index=True, max_length=20)
	payment_account=models.ForeignKey(Account,related_name='paymentMode_account')
	default=models.BooleanField('Default Payment Mode ?', default=False)
	tenant=models.ForeignKey(Tenant, related_name='paymentMode_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("name", "tenant"))
		
	def __str__(self):
		return self.name



# inventory_type_choices=(('O','Opening'),
# 			('C','Closing'))
# #This model is for opening & closing inventory
# class inventory_value(models.Model):
# 	id=models.BigAutoField(primary_key=True)
# 	inventory_type=models.CharField('Inventory type', max_length=1,choices=inventory_type_choices)
# 	accounting_period=models.ForeignKey(accounting_period, related_name='inventoryValue_accountingPeriod')
# 	tenant=models.ForeignKey(Tenant, related_name='inventoryValue_account_user_tenant')
# 	objects = TenantManager()
# 	updated = models.DateTimeField(auto_now=True)

# 	class Meta:
# 		unique_together = (("inventory_type","accounting_period", "tenant"))
		
# 	def __str__(self):
# 		return self.inventory_type

#Tax trn type: 
#1 for purchase,
#2 for sales, 
#3 for sales credit note/sales return
#4 for purchase debit note/purchase return
#5 for retail sales
#6 for retail sales credit note
#7 for service sales
#8 for service sales credit note

class tax_transaction(models.Model):
	id=models.BigAutoField(primary_key=True)
	transaction_type=models.PositiveSmallIntegerField(db_index=True) 
	tax_type=models.CharField(db_index=True, max_length=5) #CGST/SGST/IGST
	tax_percent=models.DecimalField(max_digits=5, db_index=True, decimal_places=2, default=0)
	tax_value=models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	line_wo_tax=models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	bill_value=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	customer_gst=models.CharField(max_length=20, blank=True, null=True)
	customer_state=models.CharField(max_length=4,choices=state_list, blank=True, null=True)
	# customer_name=models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	transaction_bill_id=models.BigIntegerField(db_index=True, blank=True, null=True)
	transaction_bill_no=models.CharField(db_index=True, max_length=16,blank=True, null=True)
	date=models.DateField(db_index=True)
	# is_conciled=models.BooleanField(default=False)
	is_registered=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant, related_name='taxTransaction_account_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	# class Meta:
	# 	unique_together = (("inventory_type","accounting_period", "tenant"))
		
	# def __str__(self):
	# 	return self.inventory_type