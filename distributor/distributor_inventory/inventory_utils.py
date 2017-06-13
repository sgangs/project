#from datetime import datetime
from .models import inventory_ledger
# from distributor_master.models import Product, Unit

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