from .models import WeightBasedShippingFee
from decimal import Decimal


# 合計金額計算（請求書課税方式）
def calculate_totals(cart_items, shipping):
    shipping_fee = shipping['fee']
    shipping_tax = shipping['shipping_tax']

    total_exempt = 0
    total_taxable = 0

    for item in cart_items:
        subtotal = item.product.price_per_kg * item.product.weight * item.quantity
        tax_rate = item.product.tax_rate

        if tax_rate == Decimal('0.08'):
            total_exempt += subtotal
        else:
            total_taxable += subtotal

    tax_exempt = int(total_exempt * Decimal('0.08'))
    tax_general = int((total_taxable + shipping_fee) * Decimal('0.10'))
    
    grand_total = (
        total_exempt + tax_exempt +
        total_taxable + tax_general +
        shipping_fee + shipping_tax
    )

    tax_detail = {
        'exempt': total_exempt,
        'taxable': total_taxable + shipping_fee,
        'tax_exempt': tax_exempt,
        'tax_general': tax_general,
        'shipping_fee': shipping_fee,
        'shipping_tax': shipping_tax,
    }


    return tax_detail, grand_total


# 送料計算
def calc_shipping_fee(total_weight, subtotal):
    entry = WeightBasedShippingFee.objects.filter(max_weight__gte=total_weight).order_by('max_weight').first()
    
    if not entry:
        return {
            'fee': 9999,
            'shipping_tax': 0,
            'total': 9999,
            'tax_rate': Decimal('0.1'),
        }

    # 1万円以上で送料無料
    if subtotal >= 10000:
        return {
            'fee': 0,
            'shipping_tax': 0,
            'tax_rate': 0,
            'total': 0,
        }

    fee = entry.fee
    tax_rate = entry.tax_rate
    shipping_tax = int(fee * tax_rate)
    total = fee + shipping_tax

    return {
        'fee': fee,  # 税抜
        'shipping_tax': shipping_tax,
        'tax_rate': tax_rate,
        'total': total,  # 税込
    }