from django.db import models
#from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from distribution_master.models import Manufacturer, Product, Zone, Customer, Vendor, Unit, Warehouse
from distribution_user.models import Tenant 
from distribution_accounts.models import paymentMode

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


class purchaseInvoice(models.Model):
	invoice_id = models.CharField(blank=True, max_length=12)
	slug=models.SlugField(max_length=20)
	total=models.DecimalField(max_digits=12, decimal_places=2)
	grand_discount=models.DecimalField(max_digits=10, decimal_places=2)
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	date=models.DateTimeField(default=datetime.now, blank=True)
	vendor_key=models.ForeignKey(Vendor, related_name='purchaseInvoice_purchase_master_vendor')
	warehouse=models.ForeignKey(Warehouse, related_name='purchaseInvoice_purchase_master_warehouse')
	tenant=models.ForeignKey(Tenant,related_name='purchaseInvoice_purchase_user_tenant')
	objects = TenantManager()
	#vendor_name=models.TextField(blank=True)
	
#	def get_absolute_url(self):
#		return reverse('purchaseinvoicedetail', kwargs={'detail':self.slug})

	#the save method is overriden to give unique invoice ids, slug and customer_name
	def save(self, *args, **kwargs):
		if not self.id:
			data="pi"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_invoice_number='001'
			last_invoice=type(self).objects.filter(tenant=self.tenant).\
						filter(invoice_id__contains=today_string).order_by('invoice_id').last()
			if last_invoice:
				last_invoice_number=int(last_invoice.invoice_id[8:])
				next_invoice_number='{0:03d}'.format(last_invoice_number + 1)
			self.invoice_id=data + today_string + next_invoice_number
			toslug=tenant+" " +self.invoice_id
			self.slug=slugify(toslug)

		super(purchaseInvoice, self).save(*args, **kwargs)

	class Meta:
		ordering = ('date',)

	def __str__(self):
		return  '%s %s %s' % (self.invoice_id, self.vendor_name, self.date)

	def get_absolute_url(self):
		return reverse('purchase:invoice_detail', kwargs={'detail':self.slug})


#This model is for line items of a purchase invoice
class purchaseLineItem(models.Model):
	product_name=models.CharField(max_length =200)
	product_key=models.CharField(max_length =20)
	subproduct_key=models.CharField(max_length=20)
	unit=models.CharField(max_length=20)
	manufacturer=models.CharField(max_length=20)
	#batch=models.CharField(max_length=200)
	#discount1=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	#discount2=models.DecimalField(max_digits=4, decimal_places=2, default=0)
	quantity=models.PositiveSmallIntegerField(default=0)
	free=models.PositiveSmallIntegerField(default=0)
	cost_price=models.DecimalField(max_digits=10, decimal_places=2)
	vat_type=models.CharField(max_length =15)
	vat_percent=models.DecimalField(max_digits=4, decimal_places=2)
	invoice_no=models.ForeignKey(purchaseInvoice, related_name='purchaseLineItem_purchaseInvoice')


#This stores all the individual payments made againt the invoice(s), like a ledger
class purchasePayment(models.Model):
	payment_mode=models.ForeignKey(paymentMode, related_name='purchasePayment_purchase_accounts_paymentMode')
	invoice_no=models.ForeignKey(purchaseInvoice, related_name='purchasePayment_purchaseInvoice')
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	cheque_rtgs_number=models.CharField(max_length=30, blank=True, null=True)
	collected_on=models.DateTimeField(null=True)


#This is to add debit notes of two types - Either for return of goods or for excess payment
class debitNote(models.Model):
	note_type=(('Goods Return','Goods Return'),
			('Payment Adjustment','Payment Adjustment'))
	note_id = models.CharField(blank=True, max_length=12)
	note_type=models.CharField(max_length=12,choices=note_type)
	warehouse=models.ForeignKey(Warehouse, related_name='debitNote_purchase_master_warehouse')
	vendor_key=models.ForeignKey(Vendor, related_name='debitNote_purchase_master_vendor')	
	total=models.DecimalField(max_digits=12, decimal_places=2)
	tax=models.DecimalField(max_digits=12, decimal_places=2)
	slug=models.SlugField(max_length=20)	
	date=models.DateTimeField(default=datetime.now, blank=True)	
	invoice_no=models.ForeignKey(purchaseInvoice, related_name='debitNote_purchaseInvoice', blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='debitNote_purchase_user_tenant')
	objects = TenantManager()
		
	#the save method is overriden to give unique debit note ids, slug
	def save(self, *args, **kwargs):
		if not self.id:
			data="dn"
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_note_number='001'
			last_note=type(self).objects.filter(tenant=self.tenant).\
						filter(note_id__contains=today_string).order_by('note_id').last()
			if last_note:
				last_note_number=int(last_note.note_id[8:])
				next_note_number='{0:03d}'.format(last_note_number + 1)
			self.note_id=data + today_string + next_note_number
			toslug=tenant+" " +self.note_id
			self.slug=slugify(toslug)

		super(debitNote, self).save(*args, **kwargs)

	#class Meta:
	#	ordering = ('date',)

	def __str__(self):
		return  '%s %s %s' % (self.note_id, self.vendor_name, self.date)

	def get_absolute_url(self):
		return reverse('purchase:invoice_detail', kwargs={'detail':self.slug})


#This model is for line items of a debit note for return of goods
class debitNoteLineItem(models.Model):
	inventory_type=(('Reusable','Reusable'),
			('Returnable','Returnable'),)
	product_name=models.CharField(max_length = 200)
	product_key=models.CharField(max_length = 20)
	subproduct_key=models.CharField(max_length=20)
	unit=models.CharField(max_length=20)
	quantity=models.PositiveSmallIntegerField(default=0)
	cost_price=models.DecimalField(max_digits=10, decimal_places=2)
	vat_type=models.CharField(max_length =30)
	vat_percent=models.DecimalField(max_digits=4, decimal_places=2)
	inventory_type=models.CharField(max_length=12,choices=inventory_type)
	debitnote_no=models.ForeignKey(debitNote, related_name='debitNoteLineItem_debitNote')

#This model is for line items of a debit note for excess payment
class debitNoteLineDetails(models.Model):
	details=models.TextField()
	value=models.DecimalField(max_digits=10, decimal_places=2)
	vat_percent=models.DecimalField(max_digits=4, decimal_places=2)
	debitnote_no=models.ForeignKey(debitNote, related_name='debitNoteLineDetails_debitNote')