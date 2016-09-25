from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from distribution_user.models import Tenant



choice=(('Active','Active'),
			('Inactive','Inactive'))


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)



#This is the list of manufacturers
class Manufacturer(models.Model):
	name=models.CharField(max_length=200)
	slug=models.SlugField(max_length=32)
	key=models.CharField(max_length=20)
	details=models.TextField(blank=True)
	email=models.EmailField('e-mail id',blank=True)
	status=models.CharField(max_length=10,choices=choice,default='Active')
	tenant=models.ForeignKey(Tenant,related_name='manufacturer_master_user_tenant')
	objects = TenantManager()
	
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})


	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Manufacturer, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		ordering = ('name',)
		
	def __str__(self):
		return self.name


#This is the list of units
class Unit(models.Model):
	name=models.CharField(max_length=10)
	symbol=models.CharField(max_length=10)
	slug=models.SlugField(max_length=10)
	details=models.TextField(blank=True)
	tenant=models.ForeignKey(Tenant,related_name='unit_master_user_tenant')
	objects = TenantManager()
	
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})


	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.symbol
			self.slug=slugify(item)
		super(Unit, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("symbol", "tenant"),("name", "tenant") )
		ordering = ('name',)	
		
	def __str__(self):
		return self.name


#This is the list of Product
class Product(models.Model):
	VAT_choice=(('On MRP','On MRP'),
				('On Cost Price','On Cost Price'),
				('No VAT','No VAT'),)
	name=models.CharField(max_length =200)
	unit = models.ForeignKey(Unit,related_name='product_master_master_unit')
	slug=models.SlugField(max_length=20)
	key=models.CharField('product-id', max_length=20)
	manufacturer=models.ForeignKey(Manufacturer,related_name='product_master_master_manufacturer')
	vat_type=models.CharField('VAT type', max_length=15,choices=VAT_choice,default='on cost_price')
	vat_percent=models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0)
	tenant=models.ForeignKey(Tenant,related_name='product_master_user_tenant')
	objects = TenantManager()
	#scheme=models.TextField(blank=True)
	
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Product, self).save(*args, **kwargs)

	class Meta:
		unique_together = (("key", "tenant"))
		ordering = ('name',)

	def __str__(self):
		return self.name


class subProduct(models.Model):
	product=models.ForeignKey(Product, related_name='subProduct_master_master_product')
	sub_key=models.CharField(max_length=20)
	batch=models.CharField(max_length=20, blank=True)
	cost_price=models.DecimalField(max_digits=10, decimal_places=2)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2)
	discount1=models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0)
	discount2=models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0)
	selling_price=models.DecimalField(max_digits=10, decimal_places=2)
	scheme=models.TextField(blank=True)
	objects = TenantManager()

	class Meta:
		unique_together=("sub_key","product")


	def __str__(self):
		return self.sub_key


#This is the list of Zone
class Zone (models.Model):
	name=models.CharField(max_length=50, unique=True)
	slug=models.SlugField(max_length=20)
	key=models.CharField(max_length=20, unique=True)
	details=models.TextField(blank=True)
	tenant=models.ForeignKey(Tenant,related_name='zone_master_user_tenant')
	objects = TenantManager()
	
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)

		super(Zone, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ('name',)		

	def __str__(self):
		return self.name


#This is an abstract class for customers and vendors
class AbstractCustomer(models.Model):
	name=models.CharField(max_length=200)
	slug=models.SlugField(max_length=20)
	key=models.CharField(max_length=20)
	address=models.TextField(blank=True)
	phone_no=models.TextField(blank=True)
	details=models.TextField(blank=True)
	status=models.CharField(max_length=16,choices=choice,default='Active')
	#vat_license_no=models.PositiveSmallIntegerField(blank=True, null=True)

	class Meta:
		abstract = True
	
	
#Customer Model inherits from AbstractCustomer model
class Customer (AbstractCustomer):
	zone=models.ForeignKey(Zone,related_name='customer_master_master_zone')
	cst_no=models.CharField(max_length=20, blank=True)
	vat_no=models.CharField(max_length=20, blank=True)
	tenant=models.ForeignKey(Tenant,related_name='customer_master_user_tenant')
	objects = TenantManager()

	#def cst_output(self):
		#Returns cst number and replaces None values with an empty string
    #	if self.cst_no:
    #		return self.cst_no
    #	else:
    #    	return None
    
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Customer, self).save(*args, **kwargs)
	
	class Meta:
		unique_together=("key","tenant")
		ordering = ('zone','name',)		

	def __str__(self):
		return self.name


#Vendor Model inherits from AbstractCustomer model

class Vendor (AbstractCustomer):
	tenant=models.ForeignKey(Tenant,related_name='vendor_master_user_tenant')
	objects = TenantManager()
	#vat_license_no=models.PositiveSmallIntegerField(blank=True, null=True)
	
	def get_absolute_url(self):
		return reverse('master_detail', kwargs={'detail':self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			item=self.tenant.key+" "+self.key
			self.slug=slugify(item)
		super(Vendor, self).save(*args, **kwargs)
	
	class Meta:
		unique_together=("key","tenant")		
		ordering = ('name',)		

	def __str__(self):
		return self.name




