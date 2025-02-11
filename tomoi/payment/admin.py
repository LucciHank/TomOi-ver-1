from django.contrib import admin
from .models import Transaction, TransactionItem
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'price', 'subtotal')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'user__username')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [TransactionItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (('user', 'transaction_id'), ('payment_method', 'status'))
        }),
        ('Payment Details', {
            'fields': ('amount', 'description')
        }),
        ('Additional Information', {
            'fields': ('error_message', ('created_at', 'updated_at', 'expired_at'))
        }),
    )

    def user_info(self, obj):
        return format_html(
            '<a href="{}">{} ({})</a>',
            reverse('admin:accounts_customuser_change', args=[obj.user.id]),
            obj.user.get_full_name() or obj.user.email,
            obj.user.email
        )
    user_info.short_description = 'Customer'

    def transaction_actions(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}">Cancel</a>',
                reverse('admin:cancel_transaction', args=[obj.pk])
            )
        return '-'
    transaction_actions.short_description = 'Actions'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_transactions': qs.count(),
            'total_amount': qs.aggregate(Sum('amount'))['amount__sum'] or 0,
            'completed_transactions': qs.filter(status='completed').count(),
            'failed_transactions': qs.filter(status='failed').count(),
        }
        
        response.context_data.update(metrics)
        return response 