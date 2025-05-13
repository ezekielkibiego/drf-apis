from django.urls import path
from mpesa.views import *

urlpatterns = [
    path('api/mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('api/stk-push/', stk_push, name='stk-push'),
    

]