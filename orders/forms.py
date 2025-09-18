from django import forms
from datetime import date, timedelta

class OrderForm(forms.Form):
    SHIPPING_CHOICES = [
        ('profile', '請求先住所を使う'),
        ('shipping', '配送先住所を使う'),
    ]

    shipping_choice = forms.ChoiceField(
        choices=SHIPPING_CHOICES,
        widget=forms.RadioSelect,
        label="お届け先の選択"
    )

    # お届け日（5日後から指定可能）
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        five_days_later = (date.today() + timedelta(days=5)).isoformat()
        self.fields['delivery_date'].widget.attrs['min'] = five_days_later

    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='お届け日の選択'
    )


    payment_method = forms.ChoiceField(
        choices=[('card', 'クレジットカード'), ('bank', '現金振込'), ('qr', 'QR決済')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='お支払い方法の選択'
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False,
        label="備考"
    )

    agree = forms.BooleanField(
        label='注意事項に同意します',
        required=True
    )