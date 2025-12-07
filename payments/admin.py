from django.contrib import admin
from .models import Currency, PaymentMethod, Payment, PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['provider_reference', 'payment', 'provider_status', 'transaction_date']
    list_filter = ['provider_status', 'transaction_date']
    search_fields = ['provider_reference', 'payment__reference_number', 'payment__user__email']
    date_hierarchy = 'transaction_date'
    ordering = ['-transaction_date']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "reference_number", "user", "video", "course", "booking",
        "amount", "currency", "status", "is_confirmed", "created_at"
    ]
    list_filter = ["status", "currency", "method", "is_confirmed"]
    search_fields = ["reference_number", "user__email"]
    actions = ["mark_as_confirmed"]

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(is_confirmed=True, status="Completed")
        self.message_user(request, f"{updated} payment(s) marked as confirmed ✅")
    mark_as_confirmed.short_description = "Mark selected payments as confirmed"


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'symbol', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['code', 'symbol']
    ordering = ['code']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']
