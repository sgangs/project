from django.db import models
from django.db.models import signals
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime

from distribution_master.models import subProduct

#Each subproduct is unique. Hence, we attach inventory to the subproduct
class Inventory (models.Model):
	item=models.OneToOneField(subProduct, related_name='inventory_inventory_master_subproduct')
	quantity=models.PositiveSmallIntegerField(default=0)
	
	class Meta:
		ordering = ('item',)
		
	def __str__(self):
		return self.item

#This function gets called for every new subproduct being added to subProduct.
def create_model_inventory(sender, instance, created, **kwargs):
	#Create Inventory item for every subproduct
	if created:
		Inventory.objects.create(item=instance)

#This is the signal based on which the inventory object creation works
signals.post_save.connect(create_model_inventory, sender=subProduct, weak=False, dispatch_uid='models.create_model_inventory')

