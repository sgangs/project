import datetime as dt
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify

from distributor_master.models import Product, Unit, Warehouse
from distributor_user.models import Tenant
from distributor.variable_list import transaction_choices

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This table is to maintian inventory batch wise data
class Inventory (models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product, related_name='inventory_inventory_master_product')
	warehouse=models.ForeignKey(Warehouse, related_name='inventory_inventory_master_warehouse')
	purchase_quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	quantity_available=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	purchase_date=models.DateField(db_index=True, blank=True, null=True)
	batch=models.CharField(max_length=20, blank=True, null=True)
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	purchase_price=models.DecimalField(db_index=True, max_digits=10, decimal_places=2, blank=True, null=True)
	#To consider average inventory cost
	inventory_average_cost=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	tentative_sales_price=models.DecimalField(db_index=True, max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='inventory_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# class Meta:
		# ordering = ('warehouse','item', )
		# unique_together=("item","warehouse")
	
	# def __str__(self):
	# 	return self.product


#This table is to get initial_inventory_data
class initial_inventory (models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product, related_name='initialInventory_inventory_master_product')
	warehouse=models.ForeignKey(Warehouse, related_name='initialInventory_inventory_master_warehouse')
	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)  #This will be updated as purchase_qunatity in actual inventory table
	batch=models.CharField(max_length=20, blank=True, null=True)
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	purchase_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	#To consider average inventory cost
	inventory_average_cost=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='initialInventory_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	# class Meta:
		# ordering = ('warehouse','item', )
		# unique_together=("item","warehouse")
	
	# def __str__(self):
	# 	return self.product


#This table is to maintian inventory for open sales order quantity, but not released. This products will be booked.
class inventory_reserve (models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product, related_name='inventoryReserve_inventory_master_product')
	warehouse=models.ForeignKey(Warehouse, related_name='inventoryReserve_inventory_master_warehouse')
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	quantity_reserve=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	date=models.DateField(db_index=True, blank=True, null=True)
	batch=models.CharField(max_length=20, blank=True, null=True)
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	#This will either be purchase price or weighted avg. price :
	inventory_cost=models.DecimalField(max_digits=10, decimal_places=2) 
	sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	# transaction_bill_id=models.BigIntegerField(db_index=True, blank=True, null=True) #This item has to be added as well.
	tenant=models.ForeignKey(Tenant,related_name='inventoryReserve_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	
	# class Meta:
		# ordering = ('warehouse','item', )
		# unique_together=("item","warehouse")
	
	# def __str__(self):
	# 	return self.product


#Transaction choices registered in variable list file
#This is inventory ledger of all inventories, product wise. This model stores every inventory movement.

class inventory_ledger (models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product, related_name='inventoryLedger_inventory_master_product')
	warehouse=models.ForeignKey(Warehouse, related_name='inventoryLedger_inventory_master_warehouse')	
	transaction_type=models.PositiveSmallIntegerField('Transaction type', db_index=True, choices=transaction_choices)
	date=models.DateField(db_index=True)
	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	purchase_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	#To consider average inventory cost
	inventory_average_cost=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) 
	actual_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	transaction_bill_id=models.BigIntegerField(db_index=True, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='inventoryLedger_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	# class Meta:
		# ordering = ('warehouse','item', )
		# unique_together=("item","warehouse")
	def __str__(self):
		return self.transaction_date



#This is valuation of total inventory
class warehouse_valuation (models.Model):
	id=models.BigAutoField(primary_key=True)
	warehouse=models.ForeignKey(Warehouse, related_name='warehouseValuation_inventory_master_warehouse')	
	valuation=models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tenant=models.ForeignKey(Tenant,related_name='warehouseValuation_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)
	

#Transfer of inventory from one warehoude to another
class inventory_transfer (models.Model):
	id=models.BigAutoField(primary_key=True)
	transfer_id = models.PositiveIntegerField(db_index=True)
	# product=models.ForeignKey(Product, related_name='inventoryTransfer_inventory_master_product')
	from_warehouse=models.ForeignKey(Warehouse, related_name='inventoryTransferFrom_inventory_master_warehouse')
	to_warehouse=models.ForeignKey(Warehouse, related_name='inventoryTransferTo_inventory_master_warehouse')
	initiated_on=models.DateField(db_index=True, blank=True, null=True)
	received_on=models.DateField(db_index=True, blank=True, null=True)
	total_value=models.DecimalField(db_index=True, max_digits=10, decimal_places=2, blank=True, null=True)
	in_transit=models.BooleanField(db_index=True, default=False)
	tenant=models.ForeignKey(Tenant,related_name='inventoryTransfer_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.id:
			tenant=self.tenant.key
			today=dt.date.today()
			today_string=today.strftime('%y%m%d')
			next_transfer_number='001'
			last_transfer=type(self).objects.filter(tenant=self.tenant).\
						filter(transfer_id__contains=today_string).order_by('transfer_id').last()
			if last_transfer:
				last_transfer_id=str(last_transfer.transfer_id)
				last_transfer_number=int(last_transfer_id[6:])
				next_transfer_number='{0:03d}'.format(last_transfer_number + 1)
			self.transfer_id=int(today_string + next_transfer_number)
			
		super(inventory_transfer, self).save(*args, **kwargs)

	# class Meta:
	# 	ordering = ('date',)

	def __str__(self):
		# return  '%s %s %s' % (self.receipt_id, self.vendor, self.date)
		return  '%s %s' % (self.invoice_id, self.date)

class inventory_transfer_items (models.Model):
	id=models.BigAutoField(primary_key=True)
	inventory_id=models.BigIntegerField()
	transfer=models.ForeignKey(inventory_transfer,related_name='inventoryTransferItems_inventoryTransfer')
	product=models.ForeignKey(Product, related_name='inventoryTransferItem_inventory_master_product')
	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	unit=models.ForeignKey(Unit, related_name='inventoryTransferItem_inventory_master_unit')
	purchase_date=models.DateField(blank=True, null=True)
	batch=models.CharField(max_length=20, blank=True, null=True)
	manufacturing_date=models.DateField(blank=True, null=True)
	expiry_date=models.DateField(blank=True, null=True)
	serial_no=models.CharField(max_length=100, blank=True, null=True) #This is for items with serial no
	purchase_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	#To consider average inventory cost
	inventory_average_cost=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	tentative_sales_price=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	mrp=models.DecimalField('MRP', max_digits=10, decimal_places=2, blank=True, null=True)
	tenant=models.ForeignKey(Tenant,related_name='inventoryTransferItem_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)


class inventory_wastage (models.Model):
	id=models.BigAutoField(primary_key=True)
	product=models.ForeignKey(Product, related_name='inventoryWastage_inventory_master_product')
	warehouse=models.ForeignKey(Warehouse, related_name='inventoryWastage_inventory_master_warehouse')
	purchase_price=models.DecimalField(db_index=True, max_digits=10, decimal_places=2, blank=True, null=True)
	#To consider average inventory cost
	inventory_average_cost=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	quantity=models.DecimalField(max_digits=10, decimal_places=3, default=0)
	tenant=models.ForeignKey(Tenant,related_name='inventoryWastage_inventory_user_tenant')
	objects = TenantManager()
	updated = models.DateTimeField(auto_now=True)