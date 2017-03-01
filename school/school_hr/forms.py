from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from .models import leave_type, staff_cadre

#This is for using date widget
class DateInput(forms.DateInput):
    input_type = 'date'


#This for is to adding new subject
class leaveTypeForm(forms.ModelForm):
	class Meta:
		model=leave_type
		fields = ('name','key')		
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(leaveTypeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(leaveTypeForm, self).clean()
		unique_name=cd.get('name')
		unique_key=cd.get('key')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		elif not unique_key:
			raise forms.ValidationError(error)
		else:
			try:
				data=leave_type.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Leave with same name already exists.")
			except:
				pass
			try:
				data=leave_type.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('key',"Leave with same key already exists.")
			except:
				return cd
		return cd




#This for is to adding new subject
class staffCadreForm(forms.ModelForm):
	class Meta:
		model=staff_cadre
		fields = ('name','cadre_type')		
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(staffCadreForm, self).__init__(*args, **kwargs)
		
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(staffCadreForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=staff_cadre.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Cadre with same name already exists.")
			except:
				return cd
		return cd

