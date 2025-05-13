from django.contrib import admin
from .models import MpesaRequest, MpesaResponse, MpesaCallback


@admin.register(MpesaRequest)
class MpesaRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone_number', 'amount', 'account_reference', 'transaction_desc', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('phone_number', 'account_reference', 'transaction_desc')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)


@admin.register(MpesaResponse)
class MpesaResponseAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'request', 'merchant_request_id', 'checkout_request_id',
        'response_code', 'response_description', 'customer_message', 'timestamp'
    )
    list_filter = ('timestamp', 'response_code')
    search_fields = ('merchant_request_id', 'checkout_request_id', 'response_description', 'customer_message')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

admin.site.register(MpesaCallback)
