#from datetime import datetime
from distributor_purchase.models import purchase_receipt, purchase_order, purchase_return, return_line_item
# from distributor_master.models import Product, Unit
from distributor_inventory.models import Inventory, inventory_ledger

from distributor.global_utils import new_tax_transaction_register

def new_purchase_receipt(tenant, supplier_invoice, vendor, warehouse, date, duedate, subtotal, cgsttotal, sgsttotal, igsttotal, 
		round_value, total, cash_discount = 0, amount_paid = 0, from_purchase_order = False, order_id = None, inventory_type=True):

	vendor_name=vendor.name
	ven_address=vendor.address_1+", "+vendor.address_2
	ven_state=vendor.state
	ven_city=vendor.city
	ven_pin=vendor.pin
	ven_gst=vendor.gst


	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_receipt=purchase_receipt()
	new_receipt.tenant=tenant

	new_receipt.supplier_invoice = supplier_invoice
	new_receipt.date = date
	
	new_receipt.vendor=vendor
	new_receipt.vendor_name=vendor_name
	try:
		new_receipt.vendor_address=ven_address
	except:
		new_receipt.vendor_address=''
	new_receipt.vendor_state=ven_state
	new_receipt.vendor_city=ven_city
	new_receipt.vendor_pin=ven_pin
	new_receipt.vendor_gst=ven_gst

	if (ven_gst):
		new_receipt.gst_type=1
	else:
		new_receipt.gst_type=2

	new_receipt.warehouse=warehouse
	new_receipt.warehouse_address=ware_address
	new_receipt.warehouse_state=ware_state
	new_receipt.warehouse_city=ware_city
	new_receipt.warehouse_pin=ware_pin
	
	# new_receipt.grand_discount_type=grand_discount_type
	new_receipt.grand_discount = cash_discount
	new_receipt.subtotal=subtotal
	new_receipt.cgsttotal=cgsttotal
	new_receipt.sgsttotal=sgsttotal
	new_receipt.igsttotal=igsttotal
	new_receipt.roundoff=round_value
	new_receipt.total = total
	new_receipt.duedate = duedate
	new_receipt.amount_paid = 0
	new_receipt.inventory_type = inventory_type
	if (from_purchase_order):
		new_receipt.order_id = order_id	
	new_receipt.save()
	return new_receipt


def new_purchase_order(tenant, supplier_order, vendor, warehouse, date, deliverydate,
				subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total):

	vendor_name=vendor.name
	ven_address=vendor.address_1+", "+vendor.address_2
	ven_state=vendor.state
	ven_city=vendor.city
	ven_pin=vendor.pin
	ven_gst=vendor.gst


	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_order=purchase_order()
	new_order.tenant=tenant

	new_order.supplier_order = supplier_order
	new_order.date = date
	
	new_order.vendor=vendor
	new_order.vendor_name=vendor_name
	try:
		new_order.vendor_address=ven_address
	except:
		new_order.vendor_address=''
	new_order.vendor_state=ven_state
	new_order.vendor_city=ven_city
	new_order.vendor_pin=ven_pin
	new_order.vendor_gst=ven_gst

	# if (ven_gst):
	# 	new_order.gst_type=1
	# else:
	# 	new_order.gst_type=2

	new_order.warehouse=warehouse
	new_order.warehouse_address=ware_address
	new_order.warehouse_state=ware_state
	new_order.warehouse_city=ware_city
	new_order.warehouse_pin=ware_pin
	
	# new_order.grand_discount_type=grand_discount_type
	# new_order.grand_discount_value=grand_discount_value
	new_order.subtotal=subtotal
	new_order.cgsttotal=cgsttotal
	new_order.sgsttotal=sgsttotal
	new_order.igsttotal=igsttotal
	new_order.roundoff=round_value
	new_order.total = total
	new_order.delivery_by = deliverydate
	new_order.save()
	return new_order


def new_purchase_return_inventory(tenant, supplier_note_no, vendor, warehouse, date, subtotal, cgsttotal, sgsttotal, igsttotal, 
		round_value, total, adjustmnet_receipt_no, note_type=1):

	vendor_name=vendor.name
	ven_address=vendor.address_1+", "+vendor.address_2
	ven_state=vendor.state
	ven_city=vendor.city
	ven_pin=vendor.pin
	ven_gst=vendor.gst


	ware_address=warehouse.address_1+", "+warehouse.address_2
	ware_state=warehouse.state
	ware_city=warehouse.city
	ware_pin=warehouse.pin
	
	new_receipt=purchase_return()
	new_receipt.tenant=tenant

	new_receipt.supplier_note_no = supplier_note_no
	new_receipt.adjustmnet_receipt_no = adjustmnet_receipt_no
	new_receipt.date = date
	
	new_receipt.vendor=vendor
	new_receipt.vendor_name=vendor_name
	try:
		new_receipt.vendor_address=ven_address
	except:
		new_receipt.vendor_address=''
	new_receipt.vendor_state=ven_state
	new_receipt.vendor_city=ven_city
	new_receipt.vendor_pin=ven_pin
	new_receipt.vendor_gst=ven_gst

	if (ven_gst):
		new_receipt.gst_type=1
	else:
		new_receipt.gst_type=2

	new_receipt.warehouse=warehouse
	new_receipt.warehouse_address=ware_address
	new_receipt.warehouse_state=ware_state
	new_receipt.warehouse_city=ware_city
	new_receipt.warehouse_pin=ware_pin
	
	new_receipt.subtotal=subtotal
	new_receipt.cgsttotal=cgsttotal
	new_receipt.sgsttotal=sgsttotal
	new_receipt.igsttotal=igsttotal
	new_receipt.roundoff=round_value
	new_receipt.total = total
	new_receipt.note_type = note_type
	new_receipt.save()
	return new_receipt


def new_inventory_ledger_purchase(product, warehouse, trn_type, date, quantity, pur_rate, sales_rate, invoice_id, this_tenant):
	new_inventory_ledger=inventory_ledger()
	new_inventory_ledger.product=product
	new_inventory_ledger.warehouse=warehouse
	new_inventory_ledger.transaction_type=trn_type
	new_inventory_ledger.date=date
	new_inventory_ledger.quantity=quantity
	new_inventory_ledger.actual_sales_price=sales_rate
	new_inventory_ledger.purchase_price=pur_rate
	new_inventory_ledger.transaction_bill_id=invoice_id
	new_inventory_ledger.tenant=this_tenant
	new_inventory_ledger.save()


def new_return_line_item(new_receipt, product, product_name, product_sku, product_hsn_code, cgst_p, cgst_v, sgst_p,sgst_v, igst_p, igst_v, unit,\
	unit_symbol, unit_multiplier, original_quantity, original_purchase_price, original_tentative_sales_price, original_mrp, real_purchase_price,\
	line_taxable_total, line_total, this_tenant):

	LineItem = return_line_item()
	LineItem.purchase_return = new_receipt
	LineItem.product = product
	LineItem.product_name = product_name
	LineItem.product_sku = product_sku
	LineItem.product_hsn = product_hsn_code
	LineItem.cgst_percent = cgst_p
	LineItem.cgst_value = cgst_v
	LineItem.sgst_percent = sgst_p
	LineItem.sgst_value = sgst_v
	LineItem.igst_percent = igst_p
	LineItem.igst_value = igst_v
	LineItem.unit_id = unit.id
	LineItem.unit_symbol = unit_symbol
	LineItem.unit_multi = unit_multiplier
	LineItem.quantity = original_quantity
	
	# if (product.has_batch):
	# 	LineItem.batch=batch
	# 	LineItem.manufacturing_date=manufacturing_date
	# 	LineItem.expiry_date=expiry_date
	# if (product.has_instance):
	# 	LineItem.serial_no=serial_no
	LineItem.return_purchase_price = original_purchase_price
	LineItem.tentative_sales_price = original_tentative_sales_price
	LineItem.mrp = original_mrp
	#real_purchase_price is the purchase price as per the actual purchase, based on purchase history.
	LineItem.real_purchase_price = real_purchase_price
	LineItem.line_taxable_value = line_taxable_total
	LineItem.line_total = line_total
	LineItem.tenant = this_tenant
	LineItem.save()

	return LineItem