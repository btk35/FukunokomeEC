from django.contrib import admin
from .models import Order, OrderItem, WeightBasedShippingFee

# 注文内の商品（インライン表示）
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'weight', 'quantity', 'subtotal')
    can_delete = False

# 注文管理
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'ordered_at', 'status', 'payment_status', 'payment_method',
        'subtotal', 'shipping_fee', 'total_price'
    )
    list_filter = ('status', 'payment_status', 'payment_method', 'ordered_at')
    search_fields = ('user__email', 'billing_last_name', 'billing_first_name')
    inlines = [OrderItemInline]
    readonly_fields = ('ordered_at',)

# 重量別送料設定
@admin.register(WeightBasedShippingFee)
class WeightBasedShippingFeeAdmin(admin.ModelAdmin):
    list_display = ('max_weight', 'fee', 'tax_rate')
    search_fields = ('max_weight',)

# 商品明細（単独表示も可）
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'product_price', 'weight', 'quantity', 'subtotal')
    search_fields = ('product_name',)
