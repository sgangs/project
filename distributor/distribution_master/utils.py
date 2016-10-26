from distribution_inventory.models import Inventory, returnableInventory, damagedInventory

from .models import Manufacturer, Dimension, Unit, Product, subProduct, Zone, Customer, Vendor, Warehouse
 
#This function is used to create new journal groups
def create_inventory(tenant, inv_type, subproduct, warehouse):
	if( inv_type == "new"):
		inventory=Inventory()
	elif (inv_type == "returnable"):
		inventory=returnableInventory()
	elif (inv_type == "damaged"):
		inventory=damagedInventory()
	inventory.item=subproduct
	inventory.warehouse=warehouse
	inventory.tenant=tenant
	inventory.save()

