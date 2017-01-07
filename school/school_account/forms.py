from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from .models import accounting_period, ledger_group, Account, payment_mode, journal_group, account_year


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
		model=accounting_period
		fields =('start','end','current_period',)
		widgets = {
            'start': DateInput(),
            'end': DateInput(),
        }
        #widgets = {
        #    'start': forms.DateInput(attrs={'class':'datepicker'}),
        #}


#This is for a ledger group (technically a ledger). Multiple similar accts in a ledger.
class LedgerGroupForm(forms.ModelForm):
	class Meta:
		model=ledger_group
		fields =('name',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(LedgerGroupForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(LedgerGroupForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		this_data=""
		try:
			this_data=journal_group.objects.for_tenant(self.tenant).get(name=unique_name)
			self.add_error('name',"Ledger Group with same name already exists.")
		except:
			return cd
		raise forms.ValidationError(error)
		return cd

#This form is for new accounts entry
class AccountForm(forms.ModelForm):
	class Meta:
		model=Account
		fields =('ledger_group','name','remarks','key','account_type',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(AccountForm, self).__init__(*args, **kwargs)
		self.fields['ledger_group'].queryset = ledger_group.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(AccountForm, self).clean()
		unique_key=cd.get('key')
		unique_name=cd.get('name')
		#print (unique_name)
		#ledger=cd.get('ledger_group')
		error=[]
		#this_data_key=""
		#this_data_name=""		
		# if not (unique_key or unique_name or ledger):
		# 	raise forms.ValidationError(error)
		# else:
		try:
			print ("Inside Try 1")
			this_data_key=Account.objects.for_tenant(self.tenant).get(key=unique_key)
			self.add_error('key',"Account with same key already exists.")
		except:
			pass
		try:
			print ("Inside Try 2")
			this_data_name=Account.objects.for_tenant(self.tenant).get(name=unique_name)
			self.add_error('name',"Account with same name already exists.")
		except:
			return cd

		raise forms.ValidationError(error)
		return cd

class JournalGroupForm(forms.ModelForm):
	class Meta:
		model=journal_group
		fields =('name',)
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
			this_data=journal_group.objects.for_tenant(self.tenant).get(name=unique_name)
			self.add_error('name',"Journal Group/Type with same name already exists.")
		except:
			return cd
		raise forms.ValidationError(error)
		return cd
		

#This form is for adding paymnet modes
class PaymentForm(forms.ModelForm):
	class Meta:
		model=payment_mode
		fields =('name','payment_account','default',)
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (PaymentForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['payment_account'].queryset = Account.objects.for_tenant(self.tenant).all()		
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
			this_data=payment_mode.objects.for_tenant(self.tenant).get(payment_account=account)
			self.add_error('payment_account',\
				"One account should have only one payment mode and this already has one")
		except:
			return cd
		if (default == "Yes"):
			#if (paymentMode.objects.for_tenant(self.tenant).get(default="Yes")):
			#	self.add_error('default',"Default paymeny mode already exists")
			try:
				this_data=payment_mode.objects.for_tenant(self.tenant).get(default="Yes")
				self.add_error('default',"Default paymeny mode already exists")
			except:
				return cd
		raise forms.ValidationError(error)
		return account

#Add new accounting year. This should not be live in production.
class AccountYearForm(forms.ModelForm):
	class Meta:
		model=account_year
		fields =('account','opening_debit','opening_credit','accounting_period')
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(AccountYearForm, self).__init__(*args, **kwargs)
		self.fields['account'].queryset = Account.objects.for_tenant(self.tenant).all()
		self.fields['accounting_period'].queryset = accounting_period.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	# def clean(self):
	# 	cd= super(AccountForm, self).clean()
	# 	unique_key=cd.get('account')
	# 	unique_name=cd.get('accounting_period')
	# 	#print (unique_name)
	# 	#ledger=cd.get('ledger_group')
	# 	error=[]
	# 	#this_data_key=""
	# 	#this_data_name=""		
	# 	# if not (unique_key or unique_name or ledger):
	# 	# 	raise forms.ValidationError(error)
	# 	# else:
	# 	try:
	# 		print ("Inside Try 1")
	# 		this_data_key=Account.objects.for_tenant(self.tenant).get(key=unique_key)
	# 		self.add_error('key',"Account with same key already exists.")
	# 	except:
	# 		pass
	# 	try:
	# 		print ("Inside Try 2")
	# 		this_data_name=Account.objects.for_tenant(self.tenant).get(name=unique_name)
	# 		self.add_error('name',"Account with same name already exists.")
	# 	except:
	# 		return cd

	# 	raise forms.ValidationError(error)
	# 	return cd