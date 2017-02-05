from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from .models import Subject, class_group, House, Batch, academic_year

#This is for using date widget
class DateInput(forms.DateInput):
    input_type = 'date'


#This for is to adding new subject
class SubjectForm(forms.ModelForm):
	class Meta:
		model=Subject
		fields = ('name',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(SubjectForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(SubjectForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=Subject.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Subject with name already exists.")
			except:
				return cd
		return cd

#This for is to adding new subject
class academicYearForm (forms.ModelForm):
	class Meta:
		model=academic_year
		fields = ('year','start','end','current_academic_year')
		widgets = {
            'start': DateInput(),
            'end': DateInput(),
        }
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(academicYearForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(academicYearForm, self).clean()
		year=cd.get('year')
		start=cd.get('start')
		end=cd.get('end')
		error=[]
		data=""
		if not year:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=academic_year.objects.for_tenant(self.tenant).get(year=year)
				self.add_error('year',"Academin Session with same data already exist")
			except:
				return cd
			try:
				start=academic_year.objects.for_tenant(self.tenant).get(start=start)
				self.add_error('start',"Academin Session with same data already exist")
			except:
				return cd
			try:
				data=academic_year.objects.for_tenant(self.tenant).get(end=end)
				self.add_error('end',"Academin Session with same data already exist")
			except:
				return cd
		return cd

#This for is to adding new batch
class BatchForm(forms.ModelForm):
	class Meta:
		model=Batch
		fields = ('name',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(BatchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(BatchForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=Batch.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Subject with name already exists.")
			except:
				return cd
		return cd

#This for is to adding new class group
class classGroupForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (classGroupForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		# self.helper.layout = Layout(
		# 	'name','unit', 'key','manufacturer','vat_type',
  #       	AppendedText('vat_percent', '%'),)
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=class_group
		fields = ('name',)
	def clean(self):
		cd= super(classGroupForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=class_group.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Class Group with same name already exists.")
			except:
				return cd
		return cd


class HouseForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (HouseForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=House
		fields = ('name', 'house_motto',)
	def clean(self):
		cd= super(HouseForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=House.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"House with same key already exists.")
			except:
				return cd
		return cd


# class ManufacturerUpdateForm(forms.ModelForm):
# 	class Meta:
# 		model=Manufacturer
# 		fields = ('name', 'details', 'email', 'status',)
# 		model.details = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
# 	def __init__(self, *args, **kwargs):
# 		self.tenant=kwargs.pop('tenant',None)
# 		super(ManufacturerUpdateForm, self).__init__(*args, **kwargs)
# 		self.helper = FormHelper(self)
# 		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-sm-2'
# 		self.helper.field_class = 'col-sm-4'


# class ProductForm(forms.ModelForm):
# 	def __init__(self,*args,**kwargs):
# 		self.tenant=kwargs.pop('tenant',None)
# 		super (ProductForm,self ).__init__(*args,**kwargs) # populates the post
# 		self.fields['manufacturer'].queryset = Manufacturer.objects.for_tenant(self.tenant).all()
# 		self.helper = FormHelper(self)
# 		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
# 		self.helper.layout = Layout(
# 			'name','unit', 'key','manufacturer','vat_type',
#         	AppendedText('vat_percent', '%'),)
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-sm-2'
# 		self.helper.field_class = 'col-sm-4'

# 	class Meta:
# 		model=Product
# 		exclude =('slug', 'tenant')
# 	def clean(self):
# 		cd= super(ProductForm, self).clean()
# 		unique_key=cd.get('key')
# 		error=[]
# 		this_key=""
# 		if not unique_key:
# 			raise forms.ValidationError(error)
# 			return cd
# 		else:
# 			try:
# 				this_key=Product.objects.for_tenant(self.tenant).get(key=unique_key)
# 				self.add_error('key',"Product with same key already exists.")
# 			except:
# 				return cd
# 				#self.add_error('key',"Product with same key already exists.")
# 		raise forms.ValidationError(error)
# 		return cd


# class ProductUpdateForm(forms.ModelForm):
# 	def __init__(self,*args,**kwargs):
# 		self.tenant=kwargs.pop('tenant',None)
# 		super (ProductUpdateForm,self ).__init__(*args,**kwargs) # populates the post
# 		self.fields['manufacturer'].queryset = Manufacturer.objects.for_tenant(self.tenant).all()
# 		self.helper = FormHelper(self)
# 		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
# 		self.helper.layout = Layout(
# 			'name','unit', 'key','manufacturer','vat_type',
#         	AppendedText('vat_percent', '%'),)
# 		self.helper.form_class = 'form-horizontal'
# 		self.helper.label_class = 'col-sm-2'
# 		self.helper.field_class = 'col-sm-4'

# 	class Meta:
# 		model=Product
# 		exclude =('slug', 'key', 'tenant')
	
