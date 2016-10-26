from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from .models import accountingPeriod, accountChart, paymentMode, journalGroup


class DateInput(forms.DateInput):
    input_type = 'date'

#This form is for adding accounting period
class PeriodForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(PeriodForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	#start = forms.DateField(widget=forms.SelectDateWidget)
	#end = forms.DateField(widget=forms.SelectDateWidget)
	class Meta:
		model=accountingPeriod
		exclude =('slug','tenant',)
		widgets = {
            'start': DateInput(),
            'end': DateInput(),
        }
        #widgets = {
        #    'start': forms.DateInput(attrs={'class':'datepicker'}),
        #}

#This form is for chart of accounts entry
class ChartForm(forms.ModelForm):
	class Meta:
		model=accountChart
		exclude =('slug','tenant',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(ChartForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(ChartForm, self).clean()
		unique_key=cd.get('key')
		unique_name=cd.get('name')
		error=[]
		this_data=""
		if not unique_key and unique_name:
			raise forms.ValidationError(error)
			return cd
		#else:
		try:
			this_data=accountChart.objects.for_tenant(self.tenant).get(key=unique_key)
			#if (this_data.name==unique_name):
			self.add_error('key',"Account with same key already exists.")
			#raise forms.ValidationError(error)
			#else:
			#	return cd
		except:
			return cd
		raise forms.ValidationError(error)
		return cd

class JournalGroupForm(forms.ModelForm):
	class Meta:
		model=journalGroup
		exclude =('slug','tenant',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(JournalGroupForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(JournalGroupForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		this_data=""
		try:
			this_data=journalGroup.objects.for_tenant(self.tenant).get(name=unique_name)
			self.add_error('name',"Journal Group/Type with same name already exists.")
		except:
			return cd
		raise forms.ValidationError(error)
		return cd
		

#This form is for adding paymnet modes
class PaymentForm(forms.ModelForm):
	class Meta:
		model=paymentMode
		exclude =('slug','tenant',)
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (PaymentForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['payment_account'].queryset = accountChart.objects.for_tenant(self.tenant).all()		
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'	
	def clean(self):
		cd= super(PaymentForm, self).clean()
		default=cd.get('default')
		account=cd.get('payment_account')
		this_data=''
		error=[]
		#if (paymentMode.objects.for_tenant(self.tenant).filter(payment_account=account)):
			#self.add_error('payment_account',"One account should have only one payment mode and this already has one")
		try:
			this_data=paymentMode.objects.for_tenant(self.tenant).get(payment_account=account)
			self.add_error('payment_account',\
				"One account should have only one payment mode and this already has one")
		except:
			return cd
		if (default == "Yes"):
			#if (paymentMode.objects.for_tenant(self.tenant).get(default="Yes")):
			#	self.add_error('default',"Default paymeny mode already exists")
			try:
				this_data=paymentMode.objects.for_tenant(self.tenant).get(default="Yes")
				self.add_error('default',"Default paymeny mode already exists")
			except:
				return cd
		raise forms.ValidationError(error)
		return account


		