import datetime as dt
from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify


from distribution_master.models import subProduct, Warehouse
from distribution_user.models import Tenant

#Each subproduct & warehouse is unique. Hence, we attach inventory to the subproduct & warehouse

#This is for fresh inventory
class Inventory (models.Model):
	item=models.ForeignKey(subProduct, related_name='inventory_inventory_master_subproduct')
	quantity=models.PositiveSmallIntegerField(default=0)
	warehouse=models.ForeignKey(Warehouse, related_name='inventory_inventory_master_warehouse')	
	tenant=models.ForeignKey(Tenant,related_name='inventory_inventory_master_user_tenant')
	class Meta:
		ordering = ('warehouse','item', )
		unique_together=("item","warehouse")
	def __str__(self):
		return self.item

#This is for returnable inventory
class returnableInventory (models.Model):
	item=models.ForeignKey(subProduct, related_name='returnableinventory_inventory_master_subproduct')
	quantity=models.PositiveSmallIntegerField(default=0)
	warehouse=models.ForeignKey(Warehouse, related_name='returnableinventory_inventory_master_warehouse')
	tenant=models.ForeignKey(Tenant,related_name='returnableinventory_inventory_master_user_tenant')
	class Meta:
		ordering = ('warehouse','item', )
		unique_together=("item","warehouse")
	def __str__(self):
		return self.item

#This is for non-returnable wasted inventory. This shall reflect as expense in account
class damagedInventory (models.Model):
	item=models.ForeignKey(subProduct, related_name='damagedinventory_inventory_master_subproduct')
	quantity=models.PositiveSmallIntegerField(default=0)
	warehouse=models.ForeignKey(Warehouse, related_name='damagedinventory_inventory_master_warehouse')
	tenant=models.ForeignKey(Tenant,related_name='damagedinventory_inventory_master_user_tenant')
	class Meta:
		ordering = ('warehouse','item', )
		unique_together=("item","warehouse")
	def __str__(self):
		return self.item




#This function gets called for every new subproduct being added to subProduct.
#def create_model_inventory(sender, instance, created, **kwargs):
	#Create Inventory item for every subproduct
#	if created:
#		Inventory.objects.create(item=instance)

#This is the signal based on which the inventory object creation works
#signals.post_save.connect(create_model_inventory, sender=subProduct, weak=False, dispatch_uid='models.create_model_inventory')

