from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum

from distributor_sales.models import sales_invoice, sales_payment, invoice_line_item
from distributor_account.models import Account, Journal, journal_entry, tax_transaction
from distributor_inventory.models import Inventory, inventory_ledger

from distributor.global_utils import new_tax_transaction_register

def new_sales_invoice_save(this_tenant, date, customer, customer_name, customer_address, customer_state, warehouse, final_save, small_large_limt, 
    subtotal, cgsttotal, sgsttotal, igsttotal, round_value, total, duedate, amount_paid, manufacturer_id = None):

    new_invoice=sales_invoice()
    new_invoice.tenant=this_tenant
    new_invoice.date = date
    
    new_invoice.customer=customer
    new_invoice.customer_name=customer_name
    new_invoice.customer_address=customer_address
    new_invoice.customer_state=customer_state
    new_invoice.customer_city=customer.city
    new_invoice.customer_pin=customer.pin
    new_invoice.customer_gst=customer.gst
    new_invoice.customer_pan=customer.pan
    new_invoice.dl_1=customer.dl_1
    new_invoice.dl_2=customer.dl_2
    
    new_invoice.manufacturer = manufacturer_id

    new_invoice.warehouse=warehouse
    ware_address=warehouse.address_1+", "+warehouse.address_2
    new_invoice.warehouse_address=ware_address
    new_invoice.warehouse_state=warehouse.state
    new_invoice.warehouse_city=warehouse.city
    new_invoice.warehouse_pin=warehouse.pin
    new_invoice.is_final=final_save
    if (customer.gst):
        new_invoice.gst_type=1
    else:
        if (subtotal<small_large_limt):
            new_invoice.gst_type=3
        else:
            new_invoice.gst_type=2
    # new_invoice.grand_discount_type=grand_discount_type
    # new_invoice.grand_discount_value=grand_discount_value
    new_invoice.subtotal=subtotal
    new_invoice.cgsttotal=cgsttotal
    new_invoice.sgsttotal=sgsttotal
    new_invoice.igsttotal=igsttotal
    new_invoice.roundoff = round_value
    new_invoice.total = total
    new_invoice.duedate = duedate
    new_invoice.amount_paid = amount_paid
    new_invoice.save()
    return new_invoice


def new_line_item(new_invoice, product, date, cgst_p, cgst_v, sgst_p, sgst_v, igst_p, igst_v, unit_symbol, unit_multiplier, 
		original_quantity, original_actual_sales_price, original_tentative_sales_price, maintain_inventory, price_list_json, original_mrp, 
		discount_type, discount_value, discount_type_2, discount_value_2, line_taxable_total, line_total, this_tenant):
	LineItem = invoice_line_item()
	LineItem.sales_invoice = new_invoice
	LineItem.product= product
	LineItem.product_name= product.name
	LineItem.product_sku=product.sku
	LineItem.product_hsn=product.hsn_code
	LineItem.date = date
	LineItem.cgst_percent=cgst_p
	LineItem.cgst_value=cgst_v
	LineItem.sgst_percent=sgst_p
	LineItem.sgst_value=sgst_v
	LineItem.igst_percent=igst_p
	LineItem.igst_value=igst_v
	LineItem.unit=unit_symbol
	LineItem.unit_multi=unit_multiplier
	LineItem.quantity=original_quantity
	# if (product.has_batch):
	# 	LineItem.batch=batch
	# 	LineItem.manufacturing_date=manufacturing_date
	# 	LineItem.expiry_date=expiry_date
	# if (product.has_instance):
	# 	LineItem.serial_no=serial_no
						
	LineItem.sales_price=original_actual_sales_price
	LineItem.tentative_sales_price=original_tentative_sales_price
	if maintain_inventory:
		LineItem.other_data=price_list_json
	LineItem.mrp=original_mrp
	LineItem.discount_type=discount_type
	LineItem.discount_value=discount_value
	LineItem.discount2_type=discount_type_2
	LineItem.discount2_value=discount_value_2
	LineItem.line_tax=line_taxable_total
	LineItem.line_total=line_total
	LineItem.tenant=this_tenant
	LineItem.save()
	return LineItem

def sales_tax_transaction(is_igst, igst_paid, cgst_paid, sgst_paid, new_invoice, date, this_tenant, is_customer_gst, customer_gst, customer_state):
	if (is_igst):
		for k,v in igst_paid.items():
			try:
				if v[2]>0:
					new_tax_transaction_register("IGST",2, k, v[0],v[1],v[2], new_invoice.id,\
						new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
			except:
				pass
	else:
		for k,v in cgst_paid.items():
			try:
				if v[2]>0:
					new_tax_transaction_register("CGST",2, k, v[0],v[1],v[2], new_invoice.id, \
						new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
			except:
				pass

		for k,v in sgst_paid.items():
			try:
				if v[2]>0:
					new_tax_transaction_register("SGST",2, k, v[0],v[1],v[2], new_invoice.id,\
						new_invoice.invoice_id, date, this_tenant, is_customer_gst, customer_gst, customer_state)
			except:
				pass

def sales_day_wise(start, end, tenant):
	sales_values=sales_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).\
			order_by('date').values('date').annotate(total=Sum('total'))
	response_data=[]
	for item in sales_values:
		response_data.append({'date':item['date'],'total':str(item['total'])})
	return response_data


def sales_raised_value(start, end, tenant):
	invoice_value=sales_invoice.objects.for_tenant(tenant).filter(date__range=(start,end)).aggregate(Sum('total'))
	return invoice_value['total__sum']

def sales_collected_value(start, end, tenant):
	payment_value=sales_payment.objects.for_tenant(tenant).filter(paid_on__range=(start,end)).aggregate(Sum('amount_received'))
	return payment_value['amount_received__sum']


def new_inventory_ledger_sales(product, warehouse, trn_type, date, quantity, pur_rate, sales_rate, invoice_id, this_tenant):
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


# def paginate_data(page_no, total_per_page, objects):
# 	response_data={}
# 	paginator = Paginator(objects, total_per_page)
# 	object_paginated=paginator.page(page_no)
			
# 	objects_list=objects[(int(page_no)-1)*total_per_page:int(page_no)*total_per_page]
# 	index = paginator.page_range.index(object_paginated.number)
# 	max_index = len(paginator.page_range)
# 	start_index = index - 3 if index >= 3 else 0

# 	end_index = index + 3 if index <= max_index - 3 else max_index
		
# 	response_data['object']=objects_list
# 	response_data['start']=start_index
# 	response_data['end']=end_index
# 	# response_data['has_previous']=paginator.has_previous()
# 	# response_data['has_next']=paginator.has_next()
# 	return response_data 

def top_distributor_product_sales(this_tenant, start, end, nos):
	invoices=sales_invoice.objects.for_tenant(this_tenant).filter(date__range=[start,end]).all()
	line_items = list(invoice_line_item.objects.filter(sales_invoice__in=invoices).values('product', 'product__name').\
					annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:nos])