from django.db import models
#from django.db.models import signals
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from distributor_master.models import Product, Customer, Unit, Warehouse, tax_structure
from distributor_user.models import Tenant 
from distributor_account.models import payment_mode

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


class sales_invoice(models.Model):
	id=models.BigAutoField(primary_key=True)
	invoice_id = models.BigIntegerField(db_index=True)
	date=models.DateField(default=dt.date.today)
	customer=models.ForeignKey(Customer,blank=True, null=True,\
						related_name='salesInvoice_sales_master_customer', on_delete=models.SET_NULL)
	customer_name=models.CharField(max_length=200)
	customer_address=models.TextField(blank=True, null=True)
	customer_state=models.CharField(max_length=4,blank=True, null=True)
	customer_city=models.CharField(max_length=50, blank=True, null=True)
	customer_pin=models.CharField(max_length=8, blank=True, null=True)
	customer_gst=models.CharField(max_length=20, blank=True, null=True)
	customer_pan=models.CharField(max_length=20, blank=True, null=True)
	dl_1=models.CharField("Drug License 1",max_length=10, blank=True, null=True)
	dl_2=models.CharField("Drug License 2", max_length=10, blank=True, null=True)
	
	warehouse=models.ForeignKey(Warehouse, blank=True, null=True,\
						related_name='salesInvoice_sales_master_warehouse', on_delete=models.SET_NULL)
	warehouse_address=models.TextField()
	warehouse_state=models.CharField(max_length=4)
	warehouse_city=models.CharField(max_length=50)
	warehouse_pin=models.CharField(max_length=8)

	is_final=models.BooleanField(default=True)
	
	#GST Type 1 means B2B registered, 2 means B2CL, 3 means B2CS.
	gst_type=models.PositiveSmallIntegerField(default=1)
	grand_discount_type=models.PositiveSmallIntegerField(default=0)
	grand_discount=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	subtotal=models.DecimalField(max_digits=12, decimal_places=2)
	taxtotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	roundoff=models.DecimalField(max_digits=3, decimal_places=2, default=0)
	total=models.DecimalField(max_digits=12, decimal_places=2)  #This includes round off
	return_value=models.DecimalField(max_digits=12, decimal_places=2, default=0)  #This is the return value
	# itemwise_discount_total=models.DecimalField(max_digits=12, decimal_places=2)
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	payable_by=models.DateField(blank=True, null=True)
	final_payment_date=models.DateField(blank=True, null=True)
	#for adding additional discount if total is not changed, update amount due/amount paid
	
	# purchase_order=models.ForeignKey(purchase_order, blank=True, null=True related_name='purchaseReceipt_purchaseOrder')
	tenant=models.ForeignKey(Tenant,related_name='salesInvoice_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	total_purchase_price=models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

#	def get_absolute_url(self):
#		return reverse('purchaseinvoicedetail', kwargs={'detail':self.slug})

	#the save method is overriden to give unique invoice ids, slug and customer_name
	def save(self, *args, **kwargs):
		if not self.id:
			# if self.tenant_id == 6:
			# 	tenant=self.tenant.key
			# 	# today=dt.date.today()
			# 	today=dt.datetime.strptime(self.date, "%Y-%m-%d").date()
			# 	today_string=today.strftime('%y%m%d')
			# 	next_invoice_number='001'
			# 	last_invoice=type(self).objects.filter(tenant=self.tenant).\
			# 				filter(invoice_id__contains=today_string).order_by('invoice_id').last()
			# 	if last_invoice:
			# 		last_invoice_id=str(last_invoice.invoice_id)
			# 		last_invoice_number=int(last_invoice_id[6:])
			# 		next_invoice_number='{0:03d}'.format(last_invoice_number + 1)
			# 	self.invoice_id=int(today_string + next_invoice_number)

		# if not self.id:
			# else:
			tenant=self.tenant.key
			today_date = datetime.strptime(self.date,'%Y-%m-%d')
			today_string = today_date.strftime('%y%m%d')
			if (today_date.month >3):
				this_year_string = today_string[:2]
				this_year_int = int(this_year_string)
				next_year_int = this_year_int+1
				next_year_string = str(next_year_int)
				today_string = this_year_string + next_year_string
			else:
				next_year_string = today_string[:2]
				next_year_int = int(next_year_string)
				this_year_int = next_year_int-1
				this_year_string = str(this_year_int)
				today_string = this_year_string + next_year_string

			mon = '{:02d}'.format(today_date.month)
			today_string+= mon

			next_invoice_number = 1
			last_invoice=type(self).objects.filter(tenant=self.tenant).\
					filter(invoice_id__contains='20'+today_string).order_by('invoice_id').last()
			
			if last_invoice:
				last_invoice_id=str(last_invoice.invoice_id)
				last_invoice_number=int(last_invoice_id[8:])
				next_invoice_number = last_invoice_number + 1
			if (next_invoice_number < 10):
				self.invoice_id = int( '20'+today_string + '00' + str(next_invoice_number))
			elif (next_invoice_number < 100):
				self.invoice_id = int( '20'+today_string + '0' + str(next_invoice_number))
			else:
				self.invoice_id = int( '20'+today_string + str(next_invoice_number))
			
		super(sales_invoice, self).save(*args, **kwargs)

	# class Meta:
	# 	ordering = ('date',)

	def __str__(self):
		# return  '%s %s %s' % (self.receipt_id, self.vendor, self.date)
		return  '%s %s' % (self.invoice_id, self.date)

	# def get_absolute_url(self):
		# return reverse('purchase:invoice_detail', kwargs={'detail':self.slug})


#This model is for line items of a purchase invoice
class invoice_line_item(models.Model):
	sales_invoice=models.ForeignKey(sales_invoice, related_name='invoiceLineItem_salesInvoice')
	product=models.ForeignKey(Product,blank=True, null=True, related_name='invoiceLineItem_sales_master_product', \
							on_delete=models.SET_NULL)
	date=models.DateField(default=dt.date.today)
	# product_pk=models.BigIntegerField(blank=True, null=True)
	product_name=models.CharField(max_length =200)
	product_sku=models.CharField(max_length =50)
	product_hsn=models.CharField(max_length=20, db_index=True, blank=True, null=True)
	vat_type=models.CharField(max_length =15)
	tax_percent=models.DecimalField(max_digits=5, decimal_places=2, default=0)

	#Add fk to unit as well.
	unit=models.CharField(max_length=20)
	unit_multi=models.DecimalField(max_digits=8, decimal_places=2, default=1)

	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	quantity_returned=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	free_without_tax=models.PositiveSmallIntegerField(default=0)
	free_with_tax=models.PositiveSmallIntegerField(default=0)
	
	batch=models.CharField(max_length=20, blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	
	sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	other_data = JSONField(blank=True, null=True)

	discount_type=models.PositiveSmallIntegerField(default=0)
	discount_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	discount2_type=models.PositiveSmallIntegerField(default=0)
	discount2_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	cgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	sgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	igst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)

	cgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	sgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	igst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	line_tax=models.DecimalField(max_digits=12, decimal_places=2)
	line_total=models.DecimalField(max_digits=12, decimal_places=2)

	
	tenant=models.ForeignKey(Tenant,related_name='invoiceLineItem_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


#This stores all the individual payments made againt the invoice(s), like a ledger
class sales_payment(models.Model):
	payment_mode=models.ForeignKey(payment_mode,blank=True, null=True,\
				related_name='salesPayment_sales_accounts_paymentMode', on_delete=models.SET_NULL)
	payment_mode_name=models.CharField('Payment Mode Name', max_length=20)
	sales_invoice=models.ForeignKey(sales_invoice, related_name='salesPayment_salesInvoice')
	amount_received=models.DecimalField(max_digits=12, decimal_places=2)
	cheque_rtgs_number=models.CharField(max_length=30, db_index=True, blank=True, null=True)
	paid_on = models.DateField(db_index=True, blank=True, null=True)
	remarks = models.CharField(max_length=200, blank=True, null=True)
	is_finalized = models.BooleanField(default=True)
	# final_payment_delay=models.PositiveSmallIntegerField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='salesPayment_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


class sales_return(models.Model):
	id=models.BigAutoField(primary_key=True)
	#Return Type:
	#1 - Registered, 2- Unregistered
	return_type = models.PositiveSmallIntegerField(default=1)
	invoice = models.ForeignKey(sales_invoice,blank=True, null=True,\
						related_name='salesReturn_salesInvoice', on_delete=models.SET_NULL)
	#Return_invoice is the adjustment invoice
	return_invoice = models.ForeignKey(sales_invoice,blank=True, null=True,\
						related_name='salesReturn_returnInvoice', on_delete=models.SET_NULL)
	return_id = models.BigIntegerField(db_index=True)
	date=models.DateField(default=dt.date.today)
	customer=models.ForeignKey(Customer,blank=True, null=True,\
						related_name='salesReturn_sales_master_customer', on_delete=models.SET_NULL)
	customer_name=models.CharField(max_length=200)
	customer_address=models.TextField(blank=True, null=True)
	customer_state=models.CharField(max_length=4,blank=True, null=True)
	customer_city=models.CharField(max_length=50, blank=True, null=True)
	customer_pin=models.CharField(max_length=8, blank=True, null=True)
	customer_gst=models.CharField(max_length=20, blank=True, null=True)
	customer_pan=models.CharField(max_length=20, blank=True, null=True)
	dl_1=models.CharField("Drug License 1",max_length=10, blank=True, null=True)
	dl_2=models.CharField("Drug License 2", max_length=10, blank=True, null=True)
	
	warehouse=models.ForeignKey(Warehouse, blank=True, null=True,\
						related_name='salesReturn_sales_master_warehouse', on_delete=models.SET_NULL)
	warehouse_address=models.TextField()
	warehouse_state=models.CharField(max_length=4)
	warehouse_city=models.CharField(max_length=50)
	warehouse_pin=models.CharField(max_length=8)
	
	subtotal=models.DecimalField(max_digits=12, decimal_places=2)
	cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	total=models.DecimalField(max_digits=12, decimal_places=2)
	# itemwise_discount_total=models.DecimalField(max_digits=12, decimal_places=2)
	# purchase_order=models.ForeignKey(purchase_order, blank=True, null=True related_name='purchaseReceipt_purchaseOrder')
	tenant=models.ForeignKey(Tenant,related_name='salesReturn_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	total_purchase_price=models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

#	def get_absolute_url(self):
#		return reverse('purchaseinvoicedetail', kwargs={'detail':self.slug})

	#the save method is overriden to give unique invoice ids, slug and customer_name
	def save(self, *args, **kwargs):
		if not self.id:
		# 	tenant=self.tenant.key
		# 	today=dt.date.today()
		# 	today_string=today.strftime('%y%m%d')
		# 	next_return_number='001'
		# 	last_return=type(self).objects.filter(tenant=self.tenant).\
		# 				filter(return_id__contains=today_string).order_by('return_id').last()
		# 	if last_return:
		# 		last_return_id=str(last_return.return_id)
		# 		last_return_number=int(last_return_id[6:])
		# 		next_return_number='{0:03d}'.format(last_return_number + 1)
		# 	self.return_id=int(today_string + next_return_number)
			
		# super(sales_return, self).save(*args, **kwargs)
			tenant=self.tenant.key
			today_date = datetime.strptime(self.date,'%Y-%m-%d')
			today_string = today_date.strftime('%y%m%d')
			if (today_date.month >3):
				this_year_string = today_string[:2]
				this_year_int = int(this_year_string)
				next_year_int = this_year_int+1
				next_year_string = str(next_year_int)
				today_string = this_year_string + next_year_string
			else:
				next_year_string = today_string[:2]
				next_year_int = int(next_year_string)
				this_year_int = next_year_int-1
				this_year_string = str(this_year_int)
				today_string = this_year_string + next_year_string

			mon = '{:02d}'.format(today_date.month)
			today_string+= mon

			next_invoice_number = 1
			last_invoice=type(self).objects.filter(tenant=self.tenant).\
					filter(return_id__contains='25'+today_string).order_by('return_id').last()
			
			if last_invoice:
				last_invoice_id=str(last_invoice.invoice_id)
				last_invoice_number=int(last_invoice_id[8:])
				next_invoice_number = last_invoice_number + 1
			if (next_invoice_number < 10):
				self.return_id = int( '25'+today_string + '00' + str(next_invoice_number))
			elif (next_invoice_number < 100):
				self.return_id = int( '25'+today_string + '0' + str(next_invoice_number))
			else:
				self.return_id = int( '25'+today_string + str(next_invoice_number))
		super(sales_return, self).save(*args, **kwargs)

	def __str__(self):
		# return  '%s %s %s' % (self.receipt_id, self.vendor, self.date)
		return  '%s %s' % (self.return_id, self.date)

	

#This model is for line items of a purchase invoice
class return_line_item(models.Model):
	sales_return=models.ForeignKey(sales_return, related_name='returnLineItem_salesReturn')
	product=models.ForeignKey(Product,blank=True, null=True, related_name='returnLineItem_sales_master_product', \
							on_delete=models.SET_NULL)
	date=models.DateField(default=dt.date.today)
	# product_pk=models.BigIntegerField(blank=True, null=True)
	product_name=models.CharField(max_length =200)
	product_sku=models.CharField(max_length =50)
	product_hsn=models.CharField(max_length=20, db_index=True, blank=True, null=True)
	# vat_type=models.CharField(max_length =15)
	# tax_percent=models.DecimalField(max_digits=5, decimal_places=2, default=0)

	unit=models.CharField(max_length=20)
	unit_multi=models.DecimalField(max_digits=8, decimal_places=2, default=1)

	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	
	batch=models.CharField(max_length=20, blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	
	return_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	other_data = JSONField(blank=True, null=True)

	cgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	sgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	igst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)

	cgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	sgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	igst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	line_tax=models.DecimalField(max_digits=12, decimal_places=2)
	line_total=models.DecimalField(max_digits=12, decimal_places=2)

	tenant=models.ForeignKey(Tenant,related_name='returnLineItem_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)



class customer_credit(models.Model):
	id=models.BigAutoField(primary_key=True)
	customer=models.ForeignKey(Customer,blank=True, null=True,\
						related_name='customerCredit_sales_master_customer')
	credit_amount=models.DecimalField(max_digits=12, decimal_places=2)
	tenant=models.ForeignKey(Tenant,related_name='customerCredit_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = (("customer", "tenant"))