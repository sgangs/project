from django import forms
from django.contrib.auth.models import User
from .models import accountingPeriod, accountChart


class DateInput(forms.DateInput):
    input_type = 'date'

class PeriodForm(forms.ModelForm):
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
        
class ChartForm(forms.ModelForm):
	class Meta:
		model=accountChart
		exclude =('slug','tenant',)
		widgets = {
            'start': DateInput(),
            'end': DateInput(),
        }
