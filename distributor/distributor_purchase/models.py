from django.db import models
#from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from distributor_master.models import Product, Vendor, Unit, Warehouse, tax_structure
from distributor_user.models import Tenant 
from distributor_account.models import payment_mode

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


class purchase_receipt(models.Model):
	id=models.BigAutoField(primary_key=True)
	receipt_id = models.PositiveIntegerField(db_index=True)
	supplier_invoice = models.CharField(max_length=200,blank=True, null=True)
	date=models.DateField(default=datetime.now)

	vendor=models.ForeignKey(Vendor,blank=True, null=True, 
						related_name='purchaseReceipt_purchase_master_vendor', on_delete=models.SET_NULL)
	vendor_name=models.CharField(db_index=True, max_length=200)
	vendor_address=models.TextField(blank=True, null=True)
	vendor_state=models.CharField(max_length=4,blank=True, null=True)
	vendor_city=models.CharField(max_length=50, blank=True, null=True)
	vendor_pin=models.CharField(max_length=8, blank=True, null=True)
	vendor_gst=models.CharField(max_length=20, blank=True, null=True)
	
	warehouse=models.ForeignKey(Warehouse,blank=True, null=True, \
						related_name='purchaseReceipt_purchase_master_warehouse', on_delete=models.SET_NULL)
	warehouse_address=models.TextField()
	warehouse_state=models.CharField(max_length=4)
	warehouse_city=models.CharField(max_length=50)
	warehouse_pin=models.CharField(max_length=8)
	
	gst_type=models.PositiveSmallIntegerField(default=1)
	grand_discount_type=models.PositiveSmallIntegerField(default=0)
	grand_discount=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	subtotal=models.DecimalField(max_digits=12, decimal_places=2)
	taxtotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	total=models.DecimalField(max_digits=12, decimal_places=2)
	# itemwise_discount_total=models.DecimalField(max_digits=12, decimal_places=2)
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	payable_by=models.DateField(blank=True, null=True)
	final_payment_date=models.DateField(blank=True, null=True)
	# purchase_order=models.ForeignKey(purchase_order, blank=True, null=True related_name='purchaseReceipt_purchaseOrder')
	tenant=models.ForeignKey(Tenant,related_name='purchaseReceipt_purchase_user_tenant')
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
			next_receipt_number='001'
			last_receipt=type(self).objects.filter(tenant=self.tenant).\
						filter(receipt_id__contains=today_string).order_by('receipt_id').last()
			if last_receipt:
				last_receipt_id=str(last_receipt.receipt_id)
				last_receipt_number=int(last_receipt_id[6:])
				next_receipt_number='{0:03d}'.format(last_receipt_number + 1)
			self.receipt_id=int(today_string + next_receipt_number)
			
		super(purchase_receipt, self).save(*args, **kwargs)

	# class Meta:
	# 	ordering = ('date',)

	def __str__(self):
		# return  '%s %s %s' % (self.receipt_id, self.vendor, self.date)
		return  '%s %s' % (self.receipt_id, self.date)

	# def get_absolute_url(self):
		# return reverse('purchase:invoice_detail', kwargs={'detail':self.slug})


#This model is for line items of a purchase invoice
class receipt_line_item(models.Model):
	purchase_receipt=models.ForeignKey(purchase_receipt, related_name='receiptLineItem_purchaseReceipt',)
	product=models.ForeignKey(Product,blank=True, null=True, related_name='receiptLineItem_purchase_master_product',\
						on_delete=models.SET_NULL)
	# product_pk=models.BigIntegerField(blank=True, null=True)
	product_name=models.CharField(max_length =200)
	product_sku=models.CharField(max_length =50)
	vat_type=models.CharField(max_length =15, blank=True, null=True)
	tax_percent=models.DecimalField(max_digits=5, decimal_places=2, default=0)

	unit=models.CharField(max_length=20)
	unit_multi=models.DecimalField(max_digits=5, decimal_places=2, default=1)

	quantity=models.PositiveSmallIntegerField(default=0)
	free_without_tax=models.PositiveSmallIntegerField(default=0)
	free_with_tax=models.PositiveSmallIntegerField(default=0)

	batch=models.CharField(max_length=20, blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	
	purchase_price=models.DecimalField(max_digits=10, decimal_places=2)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	
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
	
	tenant=models.ForeignKey(Tenant,related_name='receiptLineItem_purchase_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


#This stores all the individual payments made againt the invoice(s), like a ledger
class purchase_payment(models.Model):
	payment_mode=models.ForeignKey(payment_mode,blank=True, null=True, related_name='purchasePayment_purchase_accounts_paymentMode',\
								on_delete=models.SET_NULL)
	payment_mode_name=models.CharField('Payment Mode Name', max_length=20)
	purchase_receipt=models.ForeignKey(purchase_receipt, related_name='purchasePayment_purchaseReceipt')
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	cheque_rtgs_number=models.CharField(max_length=30, blank=True, null=True)
	paid_on=models.DateField(db_index=True, blank=True, null=True)
	remarks=models.CharField(max_length=200, blank=True, null=True)
	# final_payment_delay=models.PositiveSmallIntegerField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='purchasePayment_purchase_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


#This stores all the individual payments made againt the invoice(s), like a ledger
class payment_line_item(models.Model):
	payment_mode=models.ForeignKey(payment_mode,related_name='paymentLineItem_paymentMode')
	purchase_receipt=models.ForeignKey(purchase_receipt, related_name='paymentLineItem_purchaseReceipt')
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	tenant=models.ForeignKey(Tenant,related_name='paymentLineItem_purchase_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


# #This is to add debit notes of two types - Either for return of goods or for excess payment
class debit_note(models.Model):
	note_type=((1,'Goods Return'),
			(2,'Payment Adjustment'))
	note_id = models.CharField(blank=True, max_length=12)
	note_type=models.CharField(max_length=12,choices=note_type)
	
	supplier_invoice = models.CharField(max_length=200,blank=True, null=True)
	date=models.DateField(default=datetime.now)

	vendor=models.ForeignKey(Vendor,blank=True, null=True, 
						related_name='debitNote_purchase_master_vendor', on_delete=models.SET_NULL)
	vendor_name=models.CharField(db_index=True, max_length=200)
	vendor_address=models.TextField(blank=True, null=True)
	vendor_state=models.CharField(max_length=4,blank=True, null=True)
	vendor_city=models.CharField(max_length=50, blank=True, null=True)
	vendor_pin=models.CharField(max_length=8, blank=True, null=True)
	
	warehouse=models.ForeignKey(Warehouse,blank=True, null=True, \
						related_name='debitNote_purchase_master_warehouse', on_delete=models.SET_NULL)
	warehouse_address=models.TextField()
	warehouse_state=models.CharField(max_length=4)
	warehouse_city=models.CharField(max_length=50)
	warehouse_pin=models.CharField(max_length=8)

	subtotal=models.DecimalField(max_digits=12, decimal_places=2)
	taxtotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	total=models.DecimalField(max_digits=12, decimal_places=2)

	tenant=models.ForeignKey(Tenant,related_name='debitNote_purchase_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
		
	#the save method is overriden to give unique debit note ids, slug
	def save(self, *args, **kwargs):
		if not self.id:
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_note_number='001'
			last_note=type(self).objects.filter(tenant=self.tenant).\
						filter(note_id__contains=today_string).order_by('note_id').last()
			if last_note:
				last_note_id=str(last_note.note_id)
				last_note_number=int(last_note_id[6:])
				next_note_number='{0:03d}'.format(last_note_number + 1)
			self.note_id=int(today_string + next_note_number)

		super(debit_note, self).save(*args, **kwargs)

	#class Meta:
	#	ordering = ('date',)

	def __str__(self):
		return  '%s %s %s' % (self.note_id, self.vendor_name, self.date)


#This model is for line items of a debit note for return of goods
class debit_note_line_item(models.Model):
	# inventory_type=(('Reusable','Reusable'),
	# 		('Returnable','Returnable'),)
	debit_note=models.ForeignKey(debit_note, related_name='debitNoteLineItem_debitNote',)
	product=models.ForeignKey(Product,blank=True, null=True, related_name='debitNoteLineItem_purchase_master_product',\
						on_delete=models.SET_NULL)
	# product_pk=models.BigIntegerField(blank=True, null=True)
	product_name=models.CharField(max_length =200)
	product_sku=models.CharField(max_length =50)
	vat_type=models.CharField(max_length =15, blank=True, null=True)
	tax_percent=models.DecimalField(max_digits=5, decimal_places=2, default=0)

	unit=models.CharField(max_length=20)
	unit_multi=models.DecimalField(max_digits=5, decimal_places=2, default=1)

	quantity=models.PositiveSmallIntegerField(default=0)
	
	purchase_price=models.DecimalField(max_digits=10, decimal_places=2)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	
	cgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	sgst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	igst_percent=models.DecimalField(max_digits=4, decimal_places=2, default=0)

	cgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	sgst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)
	igst_value=models.DecimalField(max_digits=8, decimal_places=2, default=0)

	line_tax=models.DecimalField(max_digits=12, decimal_places=2)
	line_total=models.DecimalField(max_digits=12, decimal_places=2)
	
	tenant=models.ForeignKey(Tenant,related_name='debitNoteLineItem_purchase_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

# #This model is for line items of a debit note for excess payment
# class debitNoteLineDetails(models.Model):
# 	details=models.TextField()
# 	value=models.DecimalField(max_digits=10, decimal_places=2)
# 	vat_percent=models.DecimalField(max_digits=4, decimal_places=2)
# 	debitnote_no=models.ForeignKey(debitNote, related_name='debitNoteLineDetails_debitNote')