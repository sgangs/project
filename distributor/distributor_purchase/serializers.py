from rest_framework import serializers
from .models import *

class ReceiptSerializers (serializers.ModelSerializer):
	# dimension=serializers.StringRelatedField()
	class Meta:
		model = purchase_receipt
		fields = ('id','receipt_id','supplier_invoice','date','vendor_name','vendor_address','vendor_state','vendor_city',\
			'vendor_pin','warehouse_address','warehouse_state','warehouse_city','warehouse_pin','subtotal','taxtotal','total',\
			'amount_paid','payable_by')


class PaymentSerializers (serializers.ModelSerializer):
	purchase_receipt = ReceiptSerializers()
	class Meta:
		model = purchase_payment
		fields = ('id','payment_mode_name','payment_mode','purchase_receipt','amount_paid', 'cheque_rtgs_number','paid_on','remarks')



class ReturnLineItemSerializers (serializers.ModelSerializer):
	class Meta:
		model = return_line_item
		# fields = ('id','payment_mode_name','payment_mode','purchase_receipt','amount_paid', 'cheque_rtgs_number','paid_on','remarks')

	def create(self, validated_data):
		return return_line_item.objects.create(**validated_data)

