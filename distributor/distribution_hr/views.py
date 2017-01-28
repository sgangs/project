from django.http import HttpResponse, Http404
from django.shortcuts import render
from datetime import datetime

from distribution_user.models import User, Tenant

from distribution_hr.forms import UserRegistrationForm


# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        #customerform = CustomerRegistrationForm(request.POST)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid():
            #Create new user
            new_user=userform.save(commit=False)
            #Validate Password
            new_user.set_password(userform.cleaned_data['password'])
            new_user.tenant=request.user.tenant
            new_user.save()
            #return render(request,'registration_success.html')
            return HttpResponse("Horray new user registered")
        else:
            error = "Yes"
            return render(request, 'registration_user.html' , {'userform': userform, 'error':error, })
    else:
        userform = UserRegistrationForm()

    return render(request,'registration_user.html', {'userform': userform,})