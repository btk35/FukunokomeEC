from django.db import models
from accounts.models import CustomUser
import re
from django.core.exceptions import ValidationError

# Create your models here.
def validate_phone_number(value):
    if not re.match(r'^\d{2,4}-\d{2,4}-\d{4}$', value):
        raise ValidationError('電話番号はハイフン付きで正しい形式で入力してください。')


class BaseAddress(models.Model):
    last_name = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    prefecture = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, blank=True)
    street_address = models.CharField(max_length=100, blank=True)
    address_detail = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number])
    label = models.CharField(max_length=20, choices=[
        ('home', '自宅'),
        ('office', '会社'),
        ('other', 'その他')
    ], default='home')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # このクラスは直接データベーステーブルを作らない（継承用の抽象クラス）

    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def full_address(self):
        return f"{self.postal_code} {self.prefecture} {self.city} {self.street_address} {self.address_detail}"


# ユーザプロフィール
class UserProfile(BaseAddress):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.label} - {self.user.email}"


# 配送先住所
class ShippingAddress(BaseAddress):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.label} - {self.user.email}"
