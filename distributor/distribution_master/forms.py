from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from .models import Manufacturer, Unit, Product, subProduct, Zone, Customer, Vendor, Warehouse


class ManufacturerForm(forms.ModelForm):
	class Meta:
		model=Manufacturer
		fields = ('name', 'key', 'details', 'email', 'status',)
		model.details = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(ManufacturerForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(ManufacturerForm, self).clean()
		unique_key=cd.get('key')
		error=[]
		manufac=""
		if not unique_key:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				manufac=Manufacturer.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Manufacturer with same key already exists.")
			except:
				return cd
		return cd


class ManufacturerUpdateForm(forms.ModelForm):
	class Meta:
		model=Manufacturer
		fields = ('name', 'details', 'email', 'status',)
		model.details = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(ManufacturerUpdateForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'


class UnitForm(forms.ModelForm):
	class Meta:
		model=Unit
		exclude =('slug','tenant', )
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(UnitForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(UnitForm, self).clean()
		unique_symbol=cd.get('symbol')
		unique_name=cd.get('name')
		error=[]
		symbol_blank=False
		this_sym=""
		name_blank=False
		this_name=""
		if not unique_symbol:
			symbol_blank=True
		if not unique_name:
			name_blank=True
		if (symbol_blank==False):
			try:
				this_sym=Unit.objects.for_tenant(self.tenant).get(symbol=unique_symbol)
				self.add_error('symbol',"The same symbol is already in use.")
			except:
				pass
		if (name_blank==False):
			try:
				this_sym=Unit.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"The same name is already in use.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd


	 	

class ProductForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ProductForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['unit'].queryset = Unit.objects.for_tenant(self.tenant).all()
		self.fields['manufacturer'].queryset = Manufacturer.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.layout = Layout(
			'name','unit', 'key','manufacturer','vat_type',
        	AppendedText('vat_percent', '%'),)
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Product
		exclude =('slug', 'tenant')
	def clean(self):
		cd= super(ProductForm, self).clean()
		unique_key=cd.get('key')
		error=[]
		this_key=""
		if not unique_key:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				this_key=Product.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Product with same key already exists.")
			except:
				return cd
				#self.add_error('key',"Product with same key already exists.")
		raise forms.ValidationError(error)
		return cd


class ProductUpdateForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ProductUpdateForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['unit'].queryset = Unit.objects.for_tenant(self.tenant).all()
		self.fields['manufacturer'].queryset = Manufacturer.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.layout = Layout(
			'name','unit', 'key','manufacturer','vat_type',
        	AppendedText('vat_percent', '%'),)
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Product
		exclude =('slug', 'key', 'tenant')
	
class subProductForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (subProductForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['product'].queryset = Product.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	class Meta:
		model=subProduct
		exclude =('scheme','tenant')
	def clean(self):
		cd= super(subProductForm, self).clean()
		unique_key=cd.get('sub_key')
		unique_product=cd.get('product')
		error=[]
		key_blank=False
		subprod=""
		try:
			product=Product.objects.filter(name=unique_product)
		except:
			product=None
		if not unique_key:
			key_blank=True
		if(product != None and not key_blank):
			try:
				subprod=subProduct.objects.filter(product=unique_product).get(sub_key=unique_key)
				self.add_error('sub_key',"Sub-product with same key already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd
		

class ZoneForm(forms.ModelForm):
	class Meta:
		model=Zone
		exclude =('slug', 'tenant',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(ZoneForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(ZoneForm, self).clean()
		unique_key=cd.get('key')
		error=[]
		this_zone=""
		if not unique_key:
			raise forms.ValidationError(error)
		else:
			try:
				this_zone=Zone.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Zone with same key already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd

class CustomerForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (CustomerForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['zone'].queryset = Zone.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	class Meta:
		model=Customer
		exclude=('slug', 'tenant',)
	def clean(self):
		cd= super(CustomerForm, self).clean()
		unique_key=cd.get('key')
		error=[]
		this_customer=""
		if not unique_key:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				this_customer=Customer.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Customer with same key already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd

class CustomerUpdateForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (CustomerUpdateForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['zone'].queryset = Zone.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	class Meta:
		model=Customer
		exclude=('slug', 'tenant', 'key')
	

class VendorForm(forms.ModelForm):
	class Meta:
		model=Vendor
		exclude =('slug','tenant',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(VendorForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.label_class = 'col-lg-2'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(VendorForm, self).clean()
		unique_key=cd.get('key')
		error=[]
		this_vendor=""
		if not unique_key:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				this_vendor=Vendor.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Vendor with same key already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd

class VendorUpdateForm(forms.ModelForm):
	class Meta:
		model=Vendor
		exclude =('slug','tenant', 'key')
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(VendorUpdateForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.label_class = 'col-lg-2'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	

class WarehouseForm(forms.ModelForm):
	class Meta:
		model=Warehouse
		exclude =('slug','tenant',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(WarehouseForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(WarehouseForm, self).clean()
		default=cd.get('default')
		unique_key=cd.get('key')
		this_data=''
		error=[]
		if (default == "Yes"):
			#if (Warehouse.objects.for_tenant(self.tenant).filter(default="Yes")):
				#self.add_error('default',"Default warehouse already exists")
			try:
				this_data=Warehouse.objects.for_tenant(self.tenant).get(default="Yes")
				self.add_error('default',"Default warehouse already exists")
			except:
				pass
		if not unique_key:
			raise forms.ValidationError(error)
			return cd
		else:
			#self.add_error('key',"Warehouse with same key already exists.")
			try:
				this_data=Warehouse.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Warehouse with same key already exists.")
			except:
				return cd

		raise forms.ValidationError(error)
		return cd

class WarehouseUpdateForm(forms.ModelForm):
	class Meta:
		model=Warehouse
		exclude =('slug','tenant', 'key')
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(WarehouseForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		#self.helper.form_id = 'id-UnitForm-trying'
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(WarehouseUpdateForm, self).clean()
		default=cd.get('default')
		unique_key=cd.get('key')
		this_data=''
		error=[]
		if (default == "Yes"):
			try:
				this_data=Warehouse.objects.for_tenant(self.tenant).get(default="Yes")
				self.add_error('default',"Default warehouse already exists")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd