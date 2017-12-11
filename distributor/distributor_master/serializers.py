from rest_framework import serializers
from .models import *

class ZoneSerializers (serializers.ModelSerializer):
	class Meta:
		model = Zone
		fields = ('id','name','key', 'details')

class CustomerSerializers (serializers.ModelSerializer):
	zone=serializers.StringRelatedField()
	class Meta:
		model = Customer
		fields = ('id','name','key', 'address_1','address_2','state','city','pin','phone_no','cst','tin','gst','dl_1','dl_2','details','zone')

class VendorSerializers (serializers.ModelSerializer):
	class Meta:
		model = Customer
		fields = ('id','name','key', 'address_1','address_2','state','city','pin','phone_no', 'cst','tin','gst','details')


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
	manufacturer=serializers.StringRelatedField()
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


class ServiceRateSerializers (serializers.ModelSerializer):
	service=serializers.StringRelatedField()
	class Meta:
		model = service_sales_rate
		fields = ('id','service','tentative_sales_rate', 'is_tax_included')


class ServiceGroupSerializers (serializers.ModelSerializer):
	class Meta:
		model = service_group
		fields = ('id','name')


class ServiceSerializers (serializers.ModelSerializer):
	default_unit=serializers.StringRelatedField()
	# brand=serializers.StringRelatedField()
	group=serializers.StringRelatedField()
	# serviceSalesRate_service = serializers.StringRelatedField(many=True)
	rates = ServiceRateSerializers(source='serviceSalesRate_service', many=True)
	class Meta:
		model = Product
		# fields = ('id','name','sku','hsn_code', 'barcode', 'default_unit', 'brand','group','remarks', 'rates')
		fields = ('id','name','sku','hsn_code', 'default_unit', 'remarks', 'rates', 'group')


class ServiceDetailSerializers (serializers.ModelSerializer):
	default_unit=serializers.StringRelatedField()
	# brand=serializers.StringRelatedField()
	# group=serializers.StringRelatedField()
	cgst=serializers.StringRelatedField()
	sgst=serializers.StringRelatedField()
	igst=serializers.StringRelatedField()
	group=serializers.StringRelatedField()
	class Meta:
		model = Product
		# fields = ('id','name','sku', 'barcode', 'hsn_code','cgst','sgst','igst','reorder_point','manufacturer','has_batch',\
		# 	'has_instance','has_attribute','default_unit', 'brand','group','remarks')
		fields = ('id','name','sku', 'barcode', 'hsn_code','cgst','sgst','igst', 'default_unit', 'remarks', 'group')