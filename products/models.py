from django.db import models
from django.conf import settings
from decimal import Decimal

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, blank=True) 
    year = models.PositiveIntegerField(null=False)
    brand = models.CharField(max_length=50, null=False)
    is_milled = models.BooleanField(null=False)
    weight = models.DecimalField(max_digits=4, decimal_places=1, null=False)
    description = models.TextField(blank=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal(str(settings.TAX_RATE_REDUCED)),  null=False, verbose_name='税率')
    stock = models.PositiveIntegerField(null=False)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name='商品画像')
    is_recommended = models.BooleanField(default=False)
    is_discounted = models.BooleanField(default=False)

    # 農法
    ORGANIC_METHOD_CHOICES = [
        ('standard', '一般栽培'),   
        ('organic', '有機栽培'),
        ('reduced_pesticide', '減農薬栽培'),
        ('special', '特別栽培'),
        ('pesticide_free', '無農薬栽培'),
    ]
    organic_method = models.CharField(max_length=20, choices=ORGANIC_METHOD_CHOICES, null=False, default='standard')

    # パッケージ価格計算
    @property
    def total_price(self):
        return Decimal(self.price_per_kg) * Decimal(self.weight)
    
    @property
    def total_price_with_tax(self):
        return self.total_price * (1 + Decimal(self.tax_rate))

    # 登録用
    def get_display_name(self):
        return self.name if self.name else f"{self.year}年産 | {self.brand} {'白米' if self.is_milled else '玄米'} | {self.weight}kg"

    # admin表示用
    def __str__(self):
        return self.name if self.name else self.get_display_name()

    def save(self, *args, **kwargs):
        # name登録がない場合は自動生成
        if not self.name:
            self.name = self.get_display_name()
        super().save(*args, **kwargs)