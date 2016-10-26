#from django.conf import settings
from django.contrib.auth.decorators import login_required
#from django.core.mail import send_mail
from django.shortcuts import render


from distribution_master.models import Warehouse
from .models import Inventory, damagedInventory, returnableInventory

@login_required
def inventoryList(request):
	inventories=Inventory.objects.filter(item__product__tenant=request.user.tenant)
	warehouses=Warehouse.objects.for_tenant(request.user.tenant).all()
	inventory_type = "Normal"
	return render(request, 'inventory/inventory.html',{'inventories':inventories, 'warehouses': warehouses,\
		'inventory_type': inventory_type})

def returnableInventoryList(request):
	inventories=returnableInventory.objects.filter(item__product__tenant=request.user.tenant)
	warehouses=Warehouse.objects.for_tenant(request.user.tenant).all()
	inventory_type = "Returnable"
	return render(request, 'inventory/inventory.html',{'inventories':inventories, 'warehouses': warehouses,\
		'inventory_type': inventory_type})

def damagedInventoryList(request):
	inventories=damagedInventory.objects.filter(item__product__tenant=request.user.tenant)
	warehouses=Warehouse.objects.for_tenant(request.user.tenant).all()
	inventory_type = "Damaged"
	#This is just randomly checking mail
	#subject = "Jou Jagat Bandhu"
	#message = "Joy Jagat Bandhu. /n This is my first mail."
	#from_email = settings.EMAIL_HOST_USER
	#to_list = ['sayantangangs.91@gmail.com']
	#send_mail(subject, message, from_email, to_list)

	return render(request, 'inventory/inventory.html',{'inventories':inventories, 'warehouses': warehouses,\
		'inventory_type': inventory_type})
