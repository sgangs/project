from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.layout import Submit, Layout, Field, Fieldset
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)


class DateInput(forms.DateInput):
    input_type = 'date'

class UploadFileForm(forms.Form):
	# batch = forms.IntegerField()
	def __init__(self,*args,**kwargs):
		# self.tenant=kwargs.pop('tenant',None)
		super (UploadFileForm,self ).__init__(*args,**kwargs) # populates the post
		# self.fields['batch'].queryset = Batch.objects.for_tenant(self.tenant).all()
		# self.fields['batch'].empty_label = None
		# self.fields['batch'] = forms.ChoiceField(choices=[(o.id, str(o)) for o in Batch.objects.for_tenant(self.tenant)])
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	
	file = forms.FileField()
	# batch = forms.ChoiceField(choices=(), required=True)

	# def clean(self):
	# 	cd= super(UploadCustomerForm, self).clean()
	# 	batch=cd.get('batch')
	# 	try:
	# 		batch=Batch.objects.for_tenant(self.tenant).get(id=batch)			
	# 	except:
	# 		self.add_error('batch',"Selected batch is not valid.")
	# 	return cd
