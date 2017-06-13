from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.layout import Submit, Layout, Field, Fieldset

from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .models import User, Tenant





#User Registration

class UserRegistrationForm(forms.ModelForm):
	password = forms.CharField(label='Password',
	widget=forms.PasswordInput)
	password2 = forms.CharField(label='Repeat password',
	widget=forms.PasswordInput)
	phone=PhoneNumberField(widget=PhoneNumberPrefixWidget,)
	# phone=PhoneNumberField(widget=PhoneNumberInternationalFallbackWidget)


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'aadhaar_no', 'phone',)
		#widgets = {
		#'username': forms.TextInput(attrs = {'placeholder' : 'This will be your login username & cannot be changed'}),
		#'email': forms.TextInput(attrs = {'placeholder' : 'This is required to activate your account'})
		#}
		#help_texts = {
		#'email':  'This is required to activate your account and your company will be linked to this email address',
		#}
		help_texts = {
		'email': 'Your personal email address',
		'aadhaar_no':  'Your Aadhar Number',
		'phone':  'Your personal phone number',
		}

	def __init__(self,*args,**kwargs):
		super (UserRegistrationForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	def clean_password2(self):
		cd = self.cleaned_data
		if cd['password'] != cd['password2']:
			raise forms.ValidationError('Passwords don\'t match.')
		if not isinstance(cd['phone'], PhoneNumber):
			raise forms.ValidationError('This is not a phone number.')
		return cd['password2']


class CustomerRegistrationForm(forms.ModelForm):
	phone=PhoneNumberField(widget=PhoneNumberPrefixWidget,)
	class Meta:
		model = Tenant
		fields = ('name', 'pan', 'tin', 'cst', 'gst','address_1', 'address_2', 'state', 'city', 'pin', 'email', 'key', 'phone',)
		help_texts = {
		'name':  'Name of your company',
		'pan':  'PAN license number of your company - if applicable',
		'TIN':  'TIN number of your company - if applicable',
		'cst':  'CST license number of your company - if applicable',
		'gst':  'GST license number of your company - if applicable',
		'phone':  'Official phone number of your company. ',
		# 'key':  'This is a 5 letter/number alphanumeric code that will represent your company',
		}

	def __init__(self,*args,**kwargs):
		super (CustomerRegistrationForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	def clean_password2(self):
		cd = self.cleaned_data
		if not isinstance(cd['phone'], PhoneNumber):
			raise forms.ValidationError('This is not a phone number.')
		return cd['phone']




