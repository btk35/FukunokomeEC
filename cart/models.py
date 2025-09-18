from django.db import models
from django.conf import settings

# Create your models here.
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='ユーザー')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='商品')
    quantity = models.PositiveIntegerField(default=1, verbose_name='数量')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='追加日時')

    class Meta:
        verbose_name = 'カート'
        verbose_name_plural = 'カート一覧'
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='uniq_user_product')
        ]


    def __str__(self):
        return f"{self.user} - {self.product}（{self.quantity}個）"

    def get_subtotal(self):
        return self.product.total_price * self.quantity