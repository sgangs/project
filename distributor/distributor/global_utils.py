import datetime

from io import BytesIO

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from distributor_account.models import Account, tax_transaction


def paginate_data(page_no, total_per_page, objects):
	response_data={}
	paginator = Paginator(objects, total_per_page)
	object_paginated=paginator.page(page_no)
			
	objects_list=objects[(int(page_no)-1)*total_per_page:int(page_no)*total_per_page]
	index = paginator.page_range.index(object_paginated.number)
	max_index = len(paginator.page_range)
	start_index = index - 3 if index >= 3 else 0

	end_index = index + 3 if index <= max_index - 3 else max_index
		
	response_data['object']=objects_list
	response_data['start']=start_index
	response_data['end']=end_index
	# response_data['has_previous']=paginator.has_previous()
	# response_data['has_next']=paginator.has_next()
	return response_data


def new_tax_transaction_register(tax_type, trn_type, percent, tax_value, bill_value, line_wo_tax, \
					invoice_pk, invoice_id,  date, this_tenant, is_registered, customer_gst=None, customer_state = None):
	new_tax_transaction=tax_transaction()
	new_tax_transaction.transaction_type=trn_type
	new_tax_transaction.tax_type=tax_type
	new_tax_transaction.tax_percent=percent
	new_tax_transaction.tax_value=tax_value
	new_tax_transaction.bill_value=bill_value
	new_tax_transaction.line_wo_tax=line_wo_tax
	new_tax_transaction.transaction_bill_id=invoice_pk
	new_tax_transaction.transaction_bill_no=invoice_id
	new_tax_transaction.date=date
	new_tax_transaction.tenant=this_tenant
	new_tax_transaction.is_registered = is_registered
	new_tax_transaction.customer_gst=customer_gst
	new_tax_transaction.customer_state=customer_state
	new_tax_transaction.save()

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


def daterange_list(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + datetime.timedelta(n)


