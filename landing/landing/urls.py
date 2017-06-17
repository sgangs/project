from django.conf.urls import url
from django.conf.urls import (handler400, handler403, handler404, handler500)
from django.contrib import admin

from landing_base import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view(), name='landing'),
]


#Error Handlers
handler400 = 'landing_base.views.bad_request'
handler403 = 'landing_base.views.permission_denied'
handler404 = 'landing_base.views.page_not_found'
handler500 = 'landing_base.views.server_error'