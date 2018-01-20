from rest_framework import serializers
from .models import *

class InvoiceSerializers (serializers.ModelSerializer):
	# dimension=serializers.StringRelatedField()
	class Meta:
		model = sales_invoice
		fields = ('id','invoice_id','date','customer_name','customer_address','customer_state','customer_city',\
			'customer_pin','warehouse_address','warehouse_state','warehouse_city','warehouse_pin','subtotal','taxtotal','total',\
			'amount_paid','payable_by')


class CollectionSerializers (serializers.ModelSerializer):
	sales_invoice = InvoiceSerializers()
	class Meta:
		model = sales_payment
		fields = ('id', 'payment_mode_name','payment_mode','sales_invoice','amount_received', 'cheque_rtgs_number','paid_on','remarks')

