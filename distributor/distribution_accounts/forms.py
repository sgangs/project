from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from .models import accountingPeriod, accountChart, paymentMode


class DateInput(forms.DateInput):
    input_type = 'date'

#This form is for adding accounting period
class PeriodForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
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
		super(ChartForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
		

#This form is for adding paymnet modes
class PaymentForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (PaymentForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['payment_account'].queryset = accountChart.objects.for_tenant(self.tenant).all()		
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	class Meta:
		model=paymentMode
		exclude =('slug','tenant',)
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


		