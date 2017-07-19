from rest_framework import serializers
from .models import *

class CustomerSerializers (serializers.ModelSerializer):
	class Meta:
		model = Customer
		fields = ('id','name','key', 'address_1','address_2','state','city','pin','phone_no','cst','tin','gst','details','zone')

	def update(self, instance, validated_data):
		instance.name = validated_data.get('name', instance.name)
		instance.key = validated_data.get('key', instance.key)
		instance.address_1 = validated_data.get('address_1', instance.address_1)
		instance.address_2 = validated_data.get('address_2', instance.address_2)
		instance.state = validated_data.get('state', instance.state)
		instance.city = validated_data.get('city', instance.city)
		instance.pin = validated_data.get('pin', instance.pin)
		instance.phone_no = validated_data.get('phone_no', instance.phone_no)
		instance.cst = validated_data.get('cst', instance.cst)
		instance.tin = validated_data.get('tin', instance.tin)
		instance.gst = validated_data.get('gst', instance.gst)
		instance.details = validated_data.get('details', instance.details)
		instance.zone = validated_data.get('zone', instance.zone)
		return instance

class VendorSerializers (serializers.ModelSerializer):
	class Meta:
		model = Customer
		fields = ('id','name','key', 'address_1','address_2','state','city','pin','phone_no', 'cst','tin','gst','details')


class ZoneSerializers (serializers.ModelSerializer):
	class Meta:
		model = Zone
		fields = ('id','name','key', 'details')

class TaxSerializers (serializers.ModelSerializer):
	class Meta:
		model = tax_structure
		fields = ('id','name','percentage')

class DimensionSerializers (serializers.ModelSerializer):
	class Meta:
		model = Dimension
		fields = ('id','name','details')

class UnitSerializers (serializers.ModelSerializer):
	dimension=serializers.StringRelatedField()
	class Meta:
		model = Unit
		fields = ('id','name','symbol', 'multiplier', 'dimension')

class WarehouseSerializers (serializers.ModelSerializer):
	class Meta:
		model = Warehouse
		fields = ('id','name','address_1', 'address_2', 'state', 'city', 'default',)

class AttributeSerializers (serializers.ModelSerializer):
	class Meta:
		model = Attribute
		fields = ('id','name')

class ProductRateSerializers (serializers.ModelSerializer):
	product=serializers.StringRelatedField()
	class Meta:
		model = product_sales_rate
		fields = ('id','product','tentative_sales_rate', 'is_tax_included')

class ProductSerializers (serializers.ModelSerializer):
	default_unit=serializers.StringRelatedField()
	brand=serializers.StringRelatedField()
	group=serializers.StringRelatedField()
	# productSalesRate_product = serializers.StringRelatedField(many=True)
	rates = ProductRateSerializers(source='productSalesRate_product', many=True)
	class Meta:
		model = Product
		fields = ('id','name','sku','hsn_code', 'barcode', 'default_unit', 'brand','group','remarks', 'rates')


class ProductDetailSerializers (serializers.ModelSerializer):
	default_unit=serializers.StringRelatedField()
	brand=serializers.StringRelatedField()
	group=serializers.StringRelatedField()
	cgst=serializers.StringRelatedField()
	sgst=serializers.StringRelatedField()
	igst=serializers.StringRelatedField()
	class Meta:
		model = Product
		fields = ('id','name','sku', 'barcode', 'hsn_code','cgst','sgst','igst','reorder_point','manufacturer','has_batch',\
			'has_instance','has_attribute','default_unit', 'brand','group','remarks')

class ManufacturerSerializers (serializers.ModelSerializer):
	class Meta:
		model = Manufacturer
		fields = ('id','name')

class BrandSerializers (serializers.ModelSerializer):
	manufacturer=serializers.StringRelatedField()
	class Meta:
		model = Brand
		fields = ('id','name','manufacturer')