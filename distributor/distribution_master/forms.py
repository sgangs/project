from django import forms
from django.contrib.auth.models import User
from .models import Manufacturer, Unit, Product, subProduct, Zone, Customer, Vendor
#, Account


class ManufacturerForm(forms.ModelForm):
	class Meta:
		model=Manufacturer
		fields = ('name', 'key', 'details', 'email', 'status',)
		model.details = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))

class UnitForm(forms.ModelForm):
	class Meta:
		model=Unit
		exclude =('slug','tenant', )

class ProductForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ProductForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['unit'].queryset = Unit.objects.for_tenant(self.tenant).all()
		self.fields['manufacturer'].queryset = Manufacturer.objects.for_tenant(self.tenant).all()
	class Meta:
		model=Product
		exclude =('slug', 'tenant')


class subProductForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (subProductForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['product'].queryset = Product.objects.for_tenant(self.tenant).all()
	class Meta:
		model=subProduct
		exclude =('scheme',)
		

class ZoneForm(forms.ModelForm):
	class Meta:
		model=Zone
		exclude =('slug', 'tenant',)



class CustomerForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (CustomerForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['zone'].queryset = Zone.objects.for_tenant(self.tenant).all()
	class Meta:
		model=Customer
		exclude=('slug', 'tenant',)
		#fields =('name','zone', 'key', 'address', 'phone_no', 'details', 'cst_no', 'vat_no', )

class VendorForm(forms.ModelForm):
	class Meta:
		model=Vendor
		exclude =('slug','tenant',)


#class AccountForm(forms.ModelForm):
#	class Meta:
#		model=Account
#		exclude =('slug','tenant',)

