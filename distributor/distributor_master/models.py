import datetime as dt
from datetime import datetime
from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from phonenumber_field.modelfields import PhoneNumberField

from distributor_user.models import Tenant, User
from distributor.variable_list import state_list


class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)


#This is the list of dimension, such as length, weight, numbers, etc
class Dimension(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=10)
	details=models.TextField(blank=True)
	tenant=models.ForeignKey(Tenant,related_name='dimension_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name

#This is the list of units
class Unit(models.Model):
	id=models.BigAutoField(primary_key=True)
	dimension=models.ForeignKey(Dimension,related_name='unit_dimension')
	name=models.CharField(db_index=True, max_length=30)
	symbol=models.CharField(db_index=True, max_length=10)
	multiplier=models.DecimalField(max_digits=6, decimal_places=2)	
	tenant=models.ForeignKey(Tenant,related_name='unit_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("symbol", "tenant"),("name", "tenant") )
		# ordering = ('name',)	
		
	def __str__(self):
		return self.name

class tax_structure(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	percentage=models.PositiveSmallIntegerField()
	tenant=models.ForeignKey(Tenant,related_name='taxStructure_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name


class Manufacturer(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	tenant=models.ForeignKey(Tenant,related_name='manufacturer_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name



class Attribute(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	tenant=models.ForeignKey(Tenant,related_name='attribute_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("name", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name


#Product group, example "T-Shirts", "Lipsticks"
class Group(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	tenant=models.ForeignKey(Tenant,related_name='group_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name

#Brand example "Lakme","Eva", "Axe"
class Brand(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	manufacturer=models.ForeignKey(Manufacturer,related_name='brand_manufacturer')
	tenant=models.ForeignKey(Tenant,related_name='brand_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name","manufacturer", "tenant"),)
		#ordering = ('name',)	
		
	def __str__(self):
		return self.name



#This is the list of Product
class Product(models.Model):
	#Change Tax Model
	VAT_choice=((1,'No VAT'),
				(2,'On MRP'),
				(3,'On Cost Price'),)
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length =200)
	sku=models.CharField(db_index=True, max_length=50)
	barcode=models.CharField(db_index=True, max_length=20, blank=True, null=True)
	hsn_code=models.CharField(db_index=True, max_length=20, blank=True, null=True)
	vat_type=models.PositiveSmallIntegerField('VAT type', choices=VAT_choice, default=3, blank=True, null=True)
	tax=models.ForeignKey(tax_structure, blank=True, null=True, related_name='product_vat', on_delete=models.SET_NULL)
	cgst=models.ForeignKey(tax_structure, blank=True, null=True, related_name='product_cgst', on_delete=models.SET_NULL)
	sgst=models.ForeignKey(tax_structure, blank=True, null=True, related_name='product_sgst', on_delete=models.SET_NULL)
	igst=models.ForeignKey(tax_structure, blank=True, null=True, related_name='product_igst', on_delete=models.SET_NULL)
	reorder_point=models.PositiveSmallIntegerField(default=0)
	default_unit=models.ForeignKey(Unit,blank=True, null=True, related_name='product_unit', on_delete=models.SET_NULL)
	brand=models.ForeignKey(Brand,related_name='product_brand', blank=True, null=True)
	manufacturer=models.ForeignKey(Manufacturer,related_name='product_manufacturer', \
									blank=True, null=True, on_delete=models.SET_NULL)
	group=models.ForeignKey(Group,related_name='product_group', blank=True, null=True, on_delete=models.SET_NULL)	
	has_batch=models.BooleanField(default=False)
	has_instance=models.BooleanField(default=False)
	has_attribute=models.BooleanField(default=False)
	remarks=models.CharField(max_length=200)
	is_active=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,related_name='product_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together = (("sku", "tenant"))
	# 	ordering = ('name',)

	def __str__(self):
		return self.name


class product_attribute(models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product,related_name='productAttribute_product')
	attribute=models.ForeignKey(Attribute,related_name='productAttribute_attribute')
	value=models.CharField(db_index=True, max_length=50)
	tenant=models.ForeignKey(Tenant,related_name='productAttribute_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("product", "attribute", "tenant"),)
		#ordering = ('name',)
		
	def __str__(self):
		return self.value


#This is the list of Zone
class Zone (models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=50)
	key=models.CharField(db_index=True, max_length=20)
	details=models.TextField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='zone_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together=("name","tenant")
		# ordering = ('name',)		

	def __str__(self):
		return self.name


#This is an abstract class for customers and vendors
class AbstractCustomer(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField(db_index=True, max_length=200)
	key=models.CharField(max_length=20)
	address_1=models.CharField("Address Line 1",max_length=200, blank=True, null=True)
	address_2=models.CharField("Address Line 2", max_length=200, blank=True, null=True)
	state=models.CharField(max_length=4,choices=state_list, blank=True, null=True)
	city=models.CharField("City", max_length=50, blank=True, null=True)
	pin=models.CharField("Pincode", max_length=8, blank=True, null=True)
	phone_no=PhoneNumberField(null=True, blank=True)
	cst=models.CharField(max_length=20, blank=True, null=True)
	tin=models.CharField(max_length=20, blank=True, null=True)
	gst=models.CharField(max_length=20, blank=True, null=True)
	details=models.TextField(blank=True, null=True)
	is_active=models.BooleanField(default=True)
	updated = models.DateTimeField(auto_now=True)
	#vat_license_no=models.PositiveSmallIntegerField(blank=True, null=True)

	class Meta:
		abstract = True
	
	
#Customer Model inherits from AbstractCustomer model
class Customer (AbstractCustomer):
	zone=models.ForeignKey(Zone,related_name='customer_zone', blank=True, null=True, on_delete=models.SET_NULL)
	tenant=models.ForeignKey(Tenant,related_name='customer_master_user_tenant')
	objects = TenantManager()

	#def cst_output(self):
		#Returns cst number and replaces None values with an empty string
    #	if self.cst_no:
    #		return self.cst_no
    #	else:
    #    	return None
    
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together=("key","tenant")
		# ordering = ('zone','name',)		

	def __str__(self):
		return self.name


#Vendor Model inherits from AbstractCustomer model
class Vendor (AbstractCustomer):
	tenant=models.ForeignKey(Tenant,related_name='vendor_master_user_tenant')
	objects = TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})

	class Meta:
		unique_together=("key","tenant")		
		# ordering = ('name',)		

	def __str__(self):
		return self.name

class retail_customer(models.Model):
	name=models.CharField(max_length=30)
	phone_no=PhoneNumberField(db_index=True)
	address=models.CharField(max_length=200, blank=True, null=True)
	email=models.EmailField(blank=True, null=True)
	gender=models.CharField(max_length=1) #Options are M,F,O
	age=models.PositiveSmallIntegerField(blank=True, null=True)
	dob=models.DateField(blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='retailCustomer_master_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("phone_no","tenant"))
		# ordering = ('-default','address', 'status')
		
	def __str__(self):
		return  '%s: %s, %s' % (self.name, self.phone_no, self.email)

class Warehouse(models.Model):
	name=models.CharField(max_length=30)
	address_1=models.CharField("Address Line 1",max_length=200)
	address_2=models.CharField("Address Line 2", max_length=200, blank=True, null=True)
	state=models.CharField(max_length=4,choices=state_list)
	city=models.CharField("City", max_length=50)
	pin=models.CharField("Pincode", max_length=8)
	remarks=models.TextField(blank=True, null=True)
	default=models.BooleanField('Defaul Warehouse?', default=False)
	is_active=models.BooleanField(default=True)
	is_retail_channel=models.BooleanField(default=False)
	tenant=models.ForeignKey(Tenant,related_name='warehouse_master_user_tenant')
	objects=TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("name","tenant"))
		# ordering = ('-default','address', 'status')
		
	def __str__(self):
		return  '%s %s: %s, %s' % (self.address_1, self.address_2, self.city, self.pin)

#This is used for the warehouse level permission of user
class warehouse_user(models.Model):
	warehouse=models.ManyToManyField(Warehouse)
	user=models.ForeignKey(User,related_name='warehouseUser_master_user_user')
	tenant=models.ForeignKey(Tenant,related_name='warehouseUser_master_user_tenant')
	objects=TenantManager()
	updated = models.DateTimeField(auto_now=True)

#This shall be the scheme thing
class product_sales_rate(models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product,related_name='productSalesRate_product')
	tentative_sales_rate=models.DecimalField(max_digits=12, decimal_places=2)
	is_tax_included=models.BooleanField(default=True)
	tenant=models.ForeignKey(Tenant,related_name='productSalesRate_master_user_tenant')
	objects = TenantManager()
	
	# def get_absolute_url(self):
	# 	return reverse('master:detail', kwargs={'detail':self.slug})


	class Meta:
		unique_together = (("product", "tenant"),)
		#ordering = ('name',)
	