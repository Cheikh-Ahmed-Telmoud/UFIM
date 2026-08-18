from django.urls import path
from .views import ussd_gateway_view

urlpatterns = [
    path('', ussd_gateway_view, name='ussd_gateway'),
]
