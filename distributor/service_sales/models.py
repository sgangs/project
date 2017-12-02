import datetime as dt
from datetime import datetime

from django.db import models
# from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField
# from django.template.defaultfilters import slugify

from phonenumber_field.modelfields import PhoneNumberField

from distributor_master.models import Service, retail_customer, Unit, Warehouse
from distributor_user.models import Tenant, User
from distributor_account.models import payment_mode

from .models import *

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


class service_invoice(models.Model):
	id=models.BigAutoField(primary_key=True)
	invoice_id = models.CharField(max_length=12)
	date=models.DateField(default=datetime.now)
	# customer=models.ForeignKey(retail_customer,blank=True, null=True,\
	# 					related_name='retailInvoice_retailsales_master_retailCustomer', on_delete=models.SET_NULL)
	# customer_name=models.CharField(max_length=200, blank=True, null=True,)
	# customer_address=models.CharField(max_length=200, blank=True, null=True)
	# customer_phone_no=PhoneNumberField(blank=True, null=True,)
	# customer_email=models.EmailField(blank=True, null=True)
	# customer_gender=models.CharField(max_length=1,blank=True, null=True,)
	# customer_dob=models.DateField(blank=True, null=True)
	
	warehouse=models.ForeignKey(Warehouse, blank=True, null=True,\
						related_name='serviceInvoice_retailsales_master_warehouse', on_delete=models.SET_NULL)
	warehouse_address=models.TextField()
	warehouse_state=models.CharField(max_length=4)
	warehouse_city=models.CharField(max_length=50)
	warehouse_pin=models.CharField(max_length=8)

	payment_mode_id=models.BigIntegerField(db_index=True, null=True, blank=True)
	payment_mode_name=models.CharField(max_length=20, null=True, blank=True)
	
	subtotal=models.DecimalField(max_digits=12, decimal_places=2)
	cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	# igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	total=models.DecimalField(max_digits=12, decimal_places=2)
	roundoff=models.DecimalField(max_digits=5, decimal_places=2, default=0)
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	tenant=models.ForeignKey(Tenant,related_name='serviceInvoice_sales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

#	def get_absolute_url(self):
#		return reverse('purchaseinvoicedetail', kwargs={'detail':self.slug})

	#the save method is overriden to give unique invoice ids, slug and customer_name
	def save(self, *args, **kwargs):
		if not self.id:
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_invoice_number='001'
			last_invoice=type(self).objects.filter(tenant=self.tenant).\
						filter(invoice_id__contains=today_string).order_by('invoice_id').last()
			if last_invoice:
				last_invoice_id=str(last_invoice.invoice_id)
				last_invoice_number=int(last_invoice_id[9:])
				next_invoice_number='{0:03d}'.format(last_invoice_number + 1)
			self.invoice_id=('ser' + today_string + next_invoice_number)
			
		super(service_invoice, self).save(*args, **kwargs)

	# class Meta:
	# 	ordering = ('date',)

	def __str__(self):
		# return  '%s %s %s' % (self.receipt_id, self.vendor, self.date)
		return  '%s %s' % (self.invoice_id, self.date)

	# def get_absolute_url(self):
		# return reverse('purchase:invoice_detail', kwargs={'detail':self.slug})


#This model is for line items of a purchase invoice
class invoice_line_item(models.Model):
	service_invoice=models.ForeignKey(service_invoice, related_name='invoiceLineItem_serviceInvoice')
	service=models.ForeignKey(Service,blank=True, null=True, related_name='invoiceLineItem_serviceSales_master_service', \
							on_delete=models.SET_NULL)
	# product_pk=models.BigIntegerField(blank=True, null=True)
	service_name=models.CharField(max_length =200)
	service_sku=models.CharField(max_length =20)
	service_hsn=models.CharField(db_index=True, max_length=8, blank=True, null=True)
	
	unit_id = models.BigIntegerField(blank=True, null=True)
	unit=models.CharField(max_length=20)
	unit_multi=models.DecimalField(max_digits=5, decimal_places=2, default=1)

	quantity=models.DecimalField(max_digits=7, decimal_places=3, default=0)
	quantity_returned=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	
	sales_price=models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	is_tax_included=models.BooleanField(default=False)
	# tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	# mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	other_data = JSONField(blank=True, null=True)

	discount_amount=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	cgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	sgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	igst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)

	cgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	sgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	igst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	line_before_tax=models.DecimalField(max_digits=12, decimal_places=2)
	line_total=models.DecimalField(max_digits=12, decimal_places=2)

	# This will be like: [{userid:contribution, userid_name:user's_name}, {userid:contribution, userid_name:user's_name}], where userid = pk of user
	user_details = JSONField(blank=True, null=True) 

	tenant=models.ForeignKey(Tenant,related_name='invoiceLineItem_serviceSales_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

# class invoice_line_item_user(models.Model):
# 	service_invoice = models.ForeignKey(service_invoice, related_name='invoiceLineItemUser_serviceInvoice')
# 	service = models.ForeignKey(Service,blank=True, null=True, related_name='invoiceLineItemUser_serviceSales_master_service', \
# 							on_delete=models.SET_NULL)
# 	service_line = models.ForeignKey(invoice_line_item, related_name='invoiceLineItemUser_invoiceLineItem')
# 	service_name = models.CharField(max_length =200)
# 	user = models.ForeignKey(User, related_name='invoiceLineItemUser_serviceSales_user_user')
# 	contrib = models.DecimalField(max_digits = 3, decimal_places = 1)
# 	tenant = models.ForeignKey(Tenant,related_name='invoiceLineItemUser_serviceSales_user_tenant')
# 	objects = TenantManager()
# 	updated = models.DateTimeField(auto_now=True)


