from django import forms
from distribution_user.models import User, Tenant




#User Registration

class UserRegistrationForm(forms.ModelForm):
	password = forms.CharField(label='Password',
	widget=forms.PasswordInput)
	password2 = forms.CharField(label='Repeat password',
	widget=forms.PasswordInput)

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email',)
		#widgets = {
		#'username': forms.TextInput(attrs = {'disabled' : True}),
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


