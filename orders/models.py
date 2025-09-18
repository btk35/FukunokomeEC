from django.db import models
from django.conf import settings
from profiles.models import UserProfile,ShippingAddress
import string
import random

# Create your models here.

# 注文id生成
def generate_unique_order_number():
    # A-Z,0-9
    chars = string.ascii_uppercase + string.digits
    # 重複対策
    while True:
        order_number = ''.join(random.choices(chars, k=8))
        if not Order.objects.filter(order_number=order_number).exists():
            return order_number

# 注文情報
class Order(models.Model):
    # 各choice定義
    STATUS_CHOICES = [  
        ('pending', '未発送'),
        ('shipped', '発送済'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', '未払い'),
        ('paid', '支払い済'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'クレジットカード'),
        ('bank', '現金振込'),
        ('qr', 'QR決済'),
    ]

    # 注文情報
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    shipping_fee = models.PositiveIntegerField() #履歴保持用
    shipping_tax = models.PositiveIntegerField() #履歴保持用
    delivery_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # 税抜合計
    total_price = models.PositiveIntegerField()  # 税・送料込合計

    # 発送先（履歴保持用・スナップショット）
    shipping_last_name = models.CharField(max_length=30)
    shipping_first_name = models.CharField(max_length=30)
    shipping_postal_code = models.CharField(max_length=7)
    shipping_prefecture = models.CharField(max_length=10)
    shipping_city = models.CharField(max_length=10, default='福岡県')
    shipping_street_address = models.CharField(max_length=100)
    shipping_address_detail = models.CharField(max_length=100, blank=True)
    shipping_phone_number = models.CharField(max_length=20)

    # 請求先の記録(履歴保持用・スナップショット)
    billing_last_name = models.CharField(max_length=30)
    billing_first_name = models.CharField(max_length=30)
    billing_postal_code = models.CharField(max_length=7)
    billing_prefecture = models.CharField(max_length=10)
    billing_city = models.CharField(max_length=100, default='福岡県')
    billing_street_address = models.CharField(max_length=100)
    billing_address_detail = models.CharField(max_length=100, blank=True)
    billing_phone_number = models.CharField(max_length=20)

    # 売上管理
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, editable=False, null=True)
    ordered_at = models.DateTimeField(auto_now_add=True)

    # 備考
    notes = models.TextField(blank=True, null=True)

    # 注文idがなければ生成して追加
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_unique_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"注文 {self.id}（{self.user.email}）"			

# 注文商品
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # 単価（税抜）
    weight = models.PositiveIntegerField()  # kg単位
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # 小計（税抜）

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
    
# 送料マスタ
class WeightBasedShippingFee(models.Model):
    max_weight = models.PositiveIntegerField()  # この重さ（kg）まで
    fee = models.PositiveIntegerField()
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.1)

    class Meta:
        ordering = ['max_weight']

    def __str__(self):
        return f"{self.max_weight}kgまで：{self.fee}円（税込）"