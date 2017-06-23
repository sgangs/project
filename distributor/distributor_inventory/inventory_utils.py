#from datetime import datetime
from decimal import Decimal
import xlrd
from django.db import IntegrityError, transaction

from .models import inventory_ledger, warehouse_valuation, Inventory, initial_inventory
from distributor_master.models import Product, Warehouse

def create_new_inventory_ledger(product, warehouse, transaction_type, date, quantity, purchase_price, mrp,
 						transaction_bill_id, tenant): 
	new_inventory_ledger=inventory_ledger()
	new_inventory_ledger.product=product
	new_inventory_ledger.warehouse=warehouse
	new_inventory_ledger.transaction_type=transaction_type #1
	new_inventory_ledger.date=date
	new_inventory_ledger.quantity=quantity
	new_inventory_ledger.purchase_price=purchase_price
	new_inventory_ledger.mrp=mrp
	new_inventory_ledger.transaction_bill_id=transaction_bill_id #new_receipt.receipt_id
	new_inventory_ledger.tenant=tenant
	new_inventory_ledger.save()



def oepning_inventory_validate(row, this_tenant):
    # row[4]=state_dict[state_selected]
    product_name=row[0]
    row[0]=Product.objects.for_tenant(this_tenant).get(name=product_name)
    warehouse=Warehouse.objects.for_tenant(this_tenant).get(default=True)
    row.append(warehouse)
    row.append(this_tenant)
    if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "" or row[2] == None or row[2] == "") :
        transaction.rollback()
        return HttpResponse("There is error in uploaded excel")
    return row


def opening_inventory_upload_save(excel_data, this_tenant):
	row_no=[]
	objects_opening = []
	objects_inventory = []
	total_valuation=0
	tmp = xlrd.open_workbook(file_contents=excel_data.read())
	sheet = tmp.sheet_by_index(0)
	num_rows = sheet.nrows
	warehouse=Warehouse.objects.for_tenant(this_tenant).get(default=True)
	for i in range(3, num_rows):
		row = sheet.row_values(i)
		if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "" or row[2] == None or row[2] == "") :
			row_no.append(i)
		else:
			row[0]=Product.objects.for_tenant(this_tenant).get(name=row[0])
			objects_opening.append(initial_inventory(product=row[0], quantity=row[1],purchase_price=row[2],\
					tentative_sales_price=row[3], mrp=row[4], warehouse=warehouse, tenant=this_tenant))
			objects_inventory.append(Inventory(product=row[0], quantity_available=row[1], purchase_quantity=row[1],\
					purchase_price=row[2],tentative_sales_price=row[3], mrp=row[4], warehouse=warehouse, tenant=this_tenant))
			total_valuation+=row[2]*row[1]

	with transaction.atomic():
		try:
			initial_inventory.objects.bulk_create(objects_opening)
			Inventory.objects.bulk_create(objects_inventory)
			warehouse_valuation_change=warehouse_valuation.objects.for_tenant(this_tenant).get(warehouse=warehouse)
			warehouse_valuation_change.valuation+=Decimal(total_valuation)
			warehouse_valuation_change.save()
		except:
			transaction.rollback()
		# print(row)
	return row_no