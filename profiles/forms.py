from django import forms
from .models import UserProfile, ShippingAddress

# ベース(継承元)
class BaseAddressForm(forms.ModelForm):
    class Meta:
        fields = [
            'last_name',
            'first_name',
            'postal_code',
            'prefecture',
            'city',
            'street_address',
            'address_detail',
            'phone_number',
            'label',
        ]
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'family-name'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'given-name'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '7', 'autocomplete': 'postal-code'}),
            'prefecture': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-level1'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-level2'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'street-address'}),
            'address_detail': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'address-line2'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'tel'}),
            'label': forms.Select(attrs={'class': 'form-control'}),
}
        labels = {
            'last_name': '姓',
            'first_name': '名',
            'postal_code': '郵便番号',
            'prefecture': '都道府県',
            'city': '市区町村',
            'street_address': '番地・建物名など',
            'address_detail': '部屋番号など',
            'phone_number': '電話番号',
            'label': '住所ラベル',
        }

# Metaクラスで定義しないと継承されない
# 基本フォーム
class UserProfileForm(BaseAddressForm):
    class Meta(BaseAddressForm.Meta):
        model = UserProfile

# 配送先フォーム
class ShippingAddressForm(BaseAddressForm):
    class Meta(BaseAddressForm.Meta):
        model = ShippingAddress
