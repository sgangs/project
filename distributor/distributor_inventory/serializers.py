from rest_framework import serializers
from .models import *
from distributor_master.serializers import *

class initialInventorySerializers (serializers.ModelSerializer):
	product=serializers.StringRelatedField()
	warehouse=serializers.StringRelatedField()
	# unit=serializers.StringRelatedField()
	class Meta:
		model = initial_inventory
		fields = ('id','product','warehouse', 'quantity', 'purchase_price','tentative_sales_price','mrp')

