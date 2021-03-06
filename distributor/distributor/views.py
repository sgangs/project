import datetime as date_first
import json
from datetime import datetime
#from django.conf import settings
from django.http import HttpResponse
from django.db import IntegrityError, transaction
from django.contrib.auth import authenticate,login as login_auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login, password_reset
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.utils.timezone import localtime, now
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import Context
from django.template.loader import get_template
from django.conf import settings


from rest_framework.decorators import api_view

from distributor_user.forms import UserRegistrationForm,CustomerRegistrationForm
from distributor_user.models import User, Tenant
from distributor_account.models import accounting_period, payment_mode
from distributor_inventory.models import warehouse_valuation
from distributor_master.models import Warehouse
from distributor_sales.sales_utils import sales_day_wise, sales_raised_value, sales_collected_value, top_distributor_product_sales
from retail_sales.sales_utils import retail_sales_day_wise, top_retail_product_sales
from distributor_account.account_support import get_income_expense
from distributor.variable_list import state_list

# from rest_framework import serializers as rest_framework_serializers  
# from rest_framework.response import Response as rest_framework_Response

# from rest_framework_jwt.settings import api_settings
# from rest_framework_jwt.serializers import JSONWebTokenSerializer
# from rest_framework_jwt.views import JSONWebTokenAPIView


from .user_creation import *
from .forms import revisedPasswordResetForm

#landing page
class HomeView(TemplateView):
    template_name = "index.html"

#landing page
@cache_control(private=True)
def base_landing_page(request):
    return render (request, 'index.html')

#Redirect authenticated users to landing page
def custom_login(request):
    if request.user.is_authenticated():
        # token, created = Token.objects.get_or_create(user=request.user)
        return redirect(landing)
    else:
        # if (request.method == 'POST'):
        #     username = request.POST['username']
        #     password = request.POST['password']
        #     user = authenticate(username=username, password=password)
        #     tenant = user.tenant
        #     tenant_due = tenant.paid_due
        #     if not tenant_due:
        #         tenant_due = tenant.trial_to
        #         tenant_max_due = tenant_due
        #     else:
        #         tenant_max_due = tenant_due + date_first.timedelta(days=15)
        #     today_date = datetime.today().date()
        #     #If date is due (or within 2 days of due), send mail to user.
        #     if (today_date>tenant_max_due):
        #         return HttpResponse("Can't login")
        #     else:
        #         login_auth(request, user)
        #         return redirect(landing)
        # return render(request,'registration/login.html', {'form': AuthenticationForm})
        return login(request)


# jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
# class JSONWebTokenAPIViewModified(JSONWebTokenAPIView):
#     def post(self, request, *args, **kwargs):
#         self.serializer_class = JSONWebTokenSerializer
#         serializer = self.get_serializer(data=request.data)

#         if serializer.is_valid():
#             user = serializer.object.get('user') or request.user
#             token = serializer.object.get('token')
#             # tenant = user.tenant
#             # tenant_due = tenant.paid_due
#             # if not tenant_due:
#             #     tenant_due = tenant.trial_to
#             #     tenant_max_due = tenant_due
#             # else:
#             #     tenant_max_due = tenant_due + date_first.timedelta(days=15)
#             # today_date = datetime.today().date()
#             # #If date is due (or within 2 days of due), send mail to user.
#             # if (today_date>tenant_max_due):
#             #     msg = ('Unable to log in with provided credentials. Payment expired.')
#             #     raise rest_framework_serializers.ValidationError(msg)
#             response_data = jwt_response_payload_handler(token, user, request)
#             response = rest_framework_Response(response_data)
#             if api_settings.JWT_AUTH_COOKIE:
#                 expiration = (datetime.utcnow() +
#                               api_settings.JWT_EXPIRATION_DELTA)
#                 response.set_cookie(api_settings.JWT_AUTH_COOKIE,
#                                     response.data['token'],
#                                     expires=expiration,
#                                     httponly=True)
#             return response

#         return rest_framework_Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# obtain_jwt_token_tenant_verified = JSONWebTokenAPIViewModified.as_view()

#Add one more level of authentication for forgot password. Then send the mail.
def custom_password_reset(request, from_email, subject_template_name, password_reset_form):
    form = revisedPasswordResetForm()
    if request.method == 'POST':
        form = revisedPasswordResetForm(request.POST)
        if form.is_valid():
            return password_reset(request,html_email_template_name='registration/password_reset_email.html',)
            # return HttpResponse("Wow")
    else:
        form = revisedPasswordResetForm()        
    return render(request,'registration/password_reset_form.html', {'form': form})
    
#registration page
def RegisterView(request):
    if request.method == 'POST':
        customerform = CustomerRegistrationForm(request.POST)
        userform = UserRegistrationForm(request.POST)
        if userform.is_valid() and customerform.is_valid():
            #Create new tenant
            new_tenant=customerform.save(commit=False)
            #business_name = request.data.get('business_name')
            #business_type = request.data.get('business_type')
            #pan_no = request.data.get('pan_no')
            #gst_no = request.data.get('gst_no')
            #is_inventory = request.data.get('is_inventory')
            #address_1 = request.data.get('address_1')
            #address_2 = request.data.get('address_2')
            #state = request.data.get('state')
            #city = request.data.get('city')
            #pin = request.data.get('pin')
            #official_mail = request.data.get('official_mail')
            #official_contact = request.data.get('official_contact')
            #business_id = request.data.get('business_id')
            
            #Create new user
            new_user=userform.save(commit=False)
            #first_name = request.data.get('first_name')
            #last_name = request.data.get('last_name')
            #personal_mail = request.data.get('personal_mail')
            #personal_contact = request.data.get('personal_contact')
            #username = request.data.get('username')
            #password = request.data.get('password')
            #repeat_password = request.data.get('repeat_password')
            #Validate Password
            new_user.set_password(userform.cleaned_data['password'])
            with transaction.atomic():
                try:
                    new_tenant.paid=False
                    new_tenant.trial=True
                    now_time=localtime(now()).replace(hour=0, minute=0, second=0, microsecond=0)
                    new_tenant.trial_from=now_time
                    new_tenant.trial_to=now_time+date_first.timedelta(days=30)
                    new_tenant.save()
                    new_user.tenant=new_tenant
                    new_user.user_type=["master"]
                    new_user.save()
                    #Do this after user's first login maybe.
                    warehouse=Warehouse()
                    warehouse.name="Default"
                    warehouse.address_1=new_tenant.address_1
                    warehouse.address_2=new_tenant.address_2
                    warehouse.state=new_tenant.state
                    warehouse.city=new_tenant.city
                    warehouse.pin=new_tenant.pin
                    warehouse.default=True
                    warehouse.tenant=new_tenant
                    warehouse.save()
                    valuation=warehouse_valuation()
                    valuation.warehouse=warehouse
                    valuation.tenant=new_tenant
                    valuation.save()
                    today=datetime.now()
                    if (today.month >3):
                        start_date=datetime(year=today.year, month=4, day=1)
                        end_date=datetime(year=today.year+1, month=3, day=31)
                    else:
                        start_date=datetime(year=today.year-1, month=4, day=1)
                        end_date=datetime(year=today.year, month=3, day=31)
                    period=accounting_period()
                    period.start=start_date
                    period.end=end_date
                    period.current_period=True
                    period.is_first_year=True
                    period.tenant=new_tenant
                    period.save()
                    
                    create_journal_group(new_tenant,"General")                            
                    create_journal_group(new_tenant,"Sales")
                    create_journal_group(new_tenant,"Purchase")
                    
                    
                    # create_accountChart(new_tenant,"IGST Payments",\
                    #     "Tax Expense", "IGST Payment Account", "igstpay", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"IGST Input",\
                        "Current Assets", "IGST Input Account", "igstin", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"IGST Output",\
                        "Current Liabilities", "IGST Output Account", "igstout", period, ledgername=None, is_first_year=True)
                    
                    # create_accountChart(new_tenant,"SGST Payments",\
                    #     "Tax Expense", "SGST Payment Account", "sgstpay", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"SGST Input",\
                        "Current Assets", "SGST Input Account", "sgstin", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"SGST Output",\
                        "Current Liabilities", "SGST Output Account", "sgstout", period, ledgername=None, is_first_year=True)
                    
                    # create_accountChart(new_tenant,"CGST Payments",\
                    #     "Tax Expense", "CGST Payment Account", "cgstpay", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"CGST Input",\
                        "Current Assets", "CGST Input Account", "cgstin", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"CGST Output",\
                        "Current Liabilities", "CGST Output Account", "cgstout", period, ledgername=None, is_first_year=True)
                    
                    create_accountChart(new_tenant,"Inventory Waste Expense", "Direct Expense",\
                        "Parent Inventory Wastage", "inventory waste", period, ledgername=None, is_first_year=True, is_contra=True)
                    
                    #Rounding off
                    create_accountChart(new_tenant,"Rounding Adjustment",\
                        "Direct Expense", "Rounding Adjustment Account", "round", period, ledgername=None, is_first_year=True)
                    # if not new_tenant.maintain_inventory:
                    #Purchase account only if user choses not to maintain inventory
                    create_accountChart(new_tenant,"Purchase","Direct Expense", "Purchase Account", "purchase", period, \
                        ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"Purchase Return","Direct Expense", "Purchase Return Account",\
                    "pur_return", period, ledgername=None, is_first_year=True, is_contra=True)
                    
                    cash_account=create_accountChart(new_tenant,"Cash","Current Assets", \
                        "Cash in hand account", "cash", period, ledgername=None, is_first_year=True)

                    bank_account=create_accountChart(new_tenant,"Bank","Current Assets", \
                        "Bank account", "bank", period, ledgername=None, is_first_year=True)

                    vendor_debit=create_accountChart(new_tenant, "Vendor Debit","Current Assets",\
                        "Debit Note Vendor Debit", "vd", period, ledgername=None, is_first_year=True, is_contra=True)

                    customer_credit=create_accountChart(new_tenant, "Customer Credit","Current Liabilities",\
                        "Credit Note Customer Credit", "cc", period, ledgername=None, is_first_year=True, is_contra=True)
                    
                    create_accountInventory(new_tenant, "Inventory","Current Assets",\
                        "Parent Inventory Account", "inventory", period, ledgername=None, is_first_year=True)
                    create_accountInventory(new_tenant,"Cost of Goods Sold",\
                        "Direct Expense", "Parent COGS Accounts", "cogs", period, ledgername=None, is_first_year=True)
                    
                    create_accountChart(new_tenant,"Accounts Payable",\
                        "Current Liabilities", "Parent Accounts Payable Accounts", "payable", period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"Accounts Receivable",\
                        "Current Assets", "Parent Accounts Receivable Accounts", "receivable",\
                        period, ledgername=None, is_first_year=True)
                    create_accountChart(new_tenant,"Sales","Direct Revenue", "Parent Sales Accounts", "sales",\
                        period, ledgername=None, is_first_year=True)

                    create_accountChart(new_tenant,"Sales Return","Direct Revenue", "Parent Sales Return Accounts", "sales_return",\
                        period, ledgername=None, is_first_year=True, is_contra=True)

                    create_accountChart(new_tenant,"Owner's Capital/Equity",\
                        "Equity/Owner/Capital", "Owner's Capital/Equity Account", "owncap", period, ledgername=None, is_first_year=True)
                    
                    dimension=create_dimension(new_tenant, "Number", "For numbers")
                    create_unit(new_tenant, dimension, "Number", "No", 1)
                    
                    dimension=create_dimension(new_tenant, "Length", "For measuring length")
                    create_unit(new_tenant, dimension, "Metre", "Mtr", 1)
                    
                    dimension=create_dimension(new_tenant, "Weight", "For measuring weight")
                    create_unit(new_tenant, dimension, "Gram", "gm", 1)
                    
                    payment= payment_mode()
                    payment.name="Cash"
                    payment.default=True
                    payment.tenant=new_tenant
                    payment.payment_account=cash_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="NEFT/RTGS"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=bank_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="Cheque"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=bank_account
                    payment.save()

                    payment= payment_mode()
                    payment.name="Vendor Debit"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=vendor_debit
                    payment.save()

                    payment= payment_mode()
                    payment.name="Customer Credit"
                    payment.default=False
                    payment.tenant=new_tenant
                    payment.payment_account=customer_credit
                    payment.save()
                    from_email = 'support@techassisto.com'
                    to_email = new_tenant.email
                    bcc_mail='sayantan@techassisto.com'
                    subject = "Welcome to Tech Assisto: "+new_user.first_name
                    # template = get_template('registration/welcome_email.html')
                    # context = Context({'first_name': new_user.first_name, 'last_name': new_user.last_name})
                    html_content = render_to_string('registration/welcome_email.html', {'first_name': new_user.first_name,\
                                    'last_name': new_user.last_name})
                    text_content = strip_tags(html_content)
                    # msg = EmailMessage(subject, content, from_email, [to_email],[bcc_mail] )
                    # msg.content_subtype = "html"
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email],[bcc_mail] )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                except:
                    transaction.rollback()

            return render(request,'registration_success.html')
        else:
            error = "Yes"
            return render(request, 'registration.html',{'userform': userform, \
                        'customerform': customerform,'error':error,})
    else:
        customerform = CustomerRegistrationForm()
        userform = UserRegistrationForm()

    return render(request,'registration.html', {'userform': userform, 'customerform': customerform})
    # return render(request,'signup-page.html', {'userform': userform, 'customerform': customerform})


#Add one more level of authentication for forgot password. Then send the mail.
def custom_password_reset(request, from_email, subject_template_name, password_reset_form):
    form = revisedPasswordResetForm()
    if request.method == 'POST':
        form = revisedPasswordResetForm(request.POST)
        if form.is_valid():
            return password_reset(request,html_email_template_name='registration/password_reset_email.html',)
            # return HttpResponse("Wow")
    else:
        form = revisedPasswordResetForm()        
    return render(request,'registration/password_reset_form.html', {'form': form})



@login_required
# @api_view(['GET'],)
def landing(request):
    this_tenant=request.user.tenant
    end=date_first.date.today()
    start=end-date_first.timedelta(days=30)
    start_5_days = end-date_first.timedelta(days=5)
    if (this_tenant.tenant_type == 2):
        sales_daily=retail_sales_day_wise(start, end, this_tenant)
        # top_sales = top_retail_product_sales(this_tenant, start_5_days, end, 5)
    else:
        sales_daily=sales_day_wise(start, end, this_tenant)
        # top_sales = top_distributor_product_sales(this_tenant, start_5_days, end, 5)
    invoice_value=sales_raised_value(start, end, this_tenant)
    payment_value=sales_collected_value(start, end, this_tenant)
    current_year=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
    income_expense=get_income_expense(this_tenant,4)
    
    # print(income_expense)
    return render(request,'landing.html', {'sales_daily':json.dumps(sales_daily, cls=DjangoJSONEncoder),\
            'invoice_value':json.dumps(invoice_value, cls=DjangoJSONEncoder), \
            'payment_value':json.dumps(payment_value, cls=DjangoJSONEncoder),'income_expense':json.dumps(income_expense, cls=DjangoJSONEncoder),\
            'current_account':current_year})

# @login_required
@api_view(['GET'],)
def tenant_user_metadata(request):
    this_user=request.user
    this_tenant=request.user.tenant
    state_dict=dict((x, y) for x, y in state_list)
    response_data = {}
    response_data['tenant_name']=this_tenant.name
    response_data['tenant_gst']=this_tenant.gst
    if this_tenant.address_2 == None or this_tenant.address_2 == 'null':
        response_data['tenant_address']=this_tenant.address_1
    else:
        response_data['tenant_address']=this_tenant.address_1+", "+this_tenant.address_2
    response_data['tenant_state']=state_dict[this_tenant.state]
    response_data['first_name']=this_user.first_name
    response_data['last_name']=this_user.last_name
    try:
        response_data['tenant_phone']=str(this_tenant.phone)
    except:
        response_data['tenant_phone']=''
    # x = this_user.phone
    # response_data['phone'] = x
    # print(x)
    # print(str(x))
    # print(type(x))
    jsondata = json.dumps(response_data, cls=DjangoJSONEncoder)
    return HttpResponse(jsondata)


@login_required
# @api_view(['GET'],)
def payment_landing(request):
    this_tenant=request.user.tenant
    end=date_first.date.today()
    start=end-date_first.timedelta(days=30)
    if (this_tenant.tenant_type == 2):
        sales_daily=retail_sales_day_wise(start, end, this_tenant)
    else:
        sales_daily=sales_day_wise(start, end, this_tenant)
    invoice_value=sales_raised_value(start, end, this_tenant)
    payment_value=sales_collected_value(start, end, this_tenant)
    current_year=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
    return render(request,'landing.html', {'sales_daily':json.dumps(sales_daily, cls=DjangoJSONEncoder),\
            'invoice_value':json.dumps(invoice_value, cls=DjangoJSONEncoder), \
            'payment_value':json.dumps(payment_value, cls=DjangoJSONEncoder), 'current_account':current_year})


#400 error
def bad_request(request):
    return render (request, 'error/400.html')

#403 error
def permission_denied(request):
    return render (request, 'error/403.html')

#404 error
def page_not_found(request):
    return render (request, 'error/404.html')

#500 error
def server_error(request):
    return render (request, 'error/500.html')