from django import forms
from .models import User, Tenant


#User Registration

class UserRegistrationForm(forms.ModelForm):
	password = forms.CharField(label='Password',
	widget=forms.PasswordInput)
	password2 = forms.CharField(label='Repeat password',
	widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email',)
		#widgets = {
		#'username': forms.TextInput(attrs = {'placeholder' : 'This will be your login username & cannot be changed'}),
		#'email': forms.TextInput(attrs = {'placeholder' : 'This is required to activate your account'})
		#}
		#help_texts = {
		#'email':  'This is required to activate your account and your company will be linked to this email address',
		#}

	def clean_password2(self):
		cd = self.cleaned_data
		if cd['password'] != cd['password2']:
			raise forms.ValidationError('Passwords don\'t match.')
		return cd['password2']


class CustomerRegistrationForm(forms.ModelForm):
	class Meta:
		model = Tenant
		fields = ('school_name', 'address', 'phone',)
		#help_texts = {
		#'name':  'Name of your company',
		#'address':  'Address of your company',
		#'cst':  'CST license number of your company',
		#'phone':  'Official phone number of your company. This is required to activate the account.',
		#'key':  'This is a 5 letter/number alphanumeric code that will represent your company',
		#}




