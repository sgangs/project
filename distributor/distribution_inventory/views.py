from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Inventory
from distribution_master.models import Warehouse

@login_required
def inventoryList(request):
	#inventories=Inventory.objects.all().select_related('item')
	inventories=Inventory.objects.filter(item__product__tenant=request.user.tenant)
	warehouses=Warehouse.objects.for_tenant(request.user.tenant).all()
	

	return render(request, 'inventory/inventory.html',{'inventories':inventories, 'warehouses': warehouses})
