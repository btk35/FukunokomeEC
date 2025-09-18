from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import date
from django.db import transaction
from django.contrib import messages

from cart.models import CartItem
from profiles.models import UserProfile, ShippingAddress
from .forms import OrderForm
from .utils import calculate_totals, calc_shipping_fee
from .models import Order, OrderItem

# 注文詳細入力
@login_required
def order_detail_view(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    for item in cart_items:
        item.subtotal = item.get_subtotal()

    profile, created = UserProfile.objects.get_or_create(user=user)
    if created or not profile.postal_code:
        return redirect(f"{reverse('profiles:edit_profile', args=['profile'])}?next={request.path}")

    # 配送先住所の登録があるかを判定
    shipping = ShippingAddress.objects.filter(user=user).first()
    is_shipping_registered = bool(shipping and shipping.postal_code and shipping.last_name)

    # 重量・小計・送料・税
    total_weight = sum(item.product.weight * item.quantity for item in cart_items)
    subtotal = sum(item.subtotal for item in cart_items)
    shipping_info = calc_shipping_fee(total_weight, subtotal)
    tax_detail, grand_total = calculate_totals(cart_items, shipping_info)

    # フォームとカートの内容をセッション保存してconfirmへ！
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = form.cleaned_data.copy()
            if isinstance(order_data.get("delivery_date"), date):
                order_data["delivery_date"] = order_data["delivery_date"].isoformat()

            request.session['order_data'] = order_data
            request.session['cart_ids'] = list(cart_items.values_list('id', flat=True))
            return redirect('orders:order_confirm')
    else:
        saved_data = request.session.get('order_data')
        if saved_data:
            form = OrderForm(initial=saved_data)
        else:
            initial_data = {'shipping_choice': 'shipping' if shipping else 'profile'}
            form = OrderForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'profile': profile,
        'shipping': shipping,
        'tax_detail': tax_detail,
        'total_price': grand_total,
        'total_weight': total_weight,
        'shipping_fee': shipping_info['fee'],
        'is_shipping_registered': is_shipping_registered,
    }

    return render(request, 'orders/order_detail.html', context)

# 入力内容の確認（セッション保存したものを展開）
@login_required
def order_confirm_view(request):
    order_data = request.session.get('order_data')
    cart_ids = request.session.get('cart_ids')

    if not order_data or not cart_ids:
        return redirect('orders:order_detail')  # セッションが切れていた場合はもう一度入力させる

    cart_items = CartItem.objects.filter(user=request.user, id__in=cart_ids)

    for item in cart_items:
        item.subtotal = item.get_subtotal()

    total_weight = sum(item.product.weight * item.quantity for item in cart_items)
    subtotal = sum(item.get_subtotal() for item in cart_items) #小計出す
    shipping_info = calc_shipping_fee(total_weight, subtotal)
    tax_detail, grand_total = calculate_totals(cart_items, shipping_info)

    # 住所取得
    profile = UserProfile.objects.get(user=request.user)
    shipping = ShippingAddress.objects.filter(user=request.user).first()

    context = {
        'order_data': order_data,
        'cart_items': cart_items,
        'shipping_fee': shipping_info['fee'],
        'tax_detail': tax_detail,
        'total_price': grand_total,
        'total_weight': total_weight,
        'profile': profile,
        'shipping': shipping,
    }

    return render(request, 'orders/order_confirm.html', context)


# 確定後のDB登録処理
@login_required
def order_complete_view(request):
    order_data = request.session.get('order_data')
    cart_ids = request.session.get('cart_ids')

    if not all([order_data, cart_ids]):
        return redirect('orders:order_detail')

    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist as e:
        messages.error(request, "ご登録情報をご確認ください。")
        return redirect('profiles:edit_profile')

    # 住所IDが指定されている場合、それを使う（安全性UP）
    shipping_id = order_data.get('shipping_id')
    shipping = None
    if order_data.get('shipping_choice') == 'shipping' and shipping_id:
        shipping = ShippingAddress.objects.filter(user=user, id=shipping_id).first()

    # カートアイテムと小計計算
    cart_items = CartItem.objects.filter(user=user, id__in=cart_ids)
    for item in cart_items:
        item.subtotal = item.get_subtotal()

    total_weight = sum(item.product.weight * item.quantity for item in cart_items)
    subtotal = sum(item.subtotal for item in cart_items)
    shipping_info = calc_shipping_fee(total_weight, subtotal)
    tax_detail, total_price = calculate_totals(cart_items, shipping_info)

    # begin transaction
    try:
        with transaction.atomic():
            order = Order.objects.create( # INSERT
                user=user,
                shipping_address=shipping,
                shipping_fee=shipping_info['fee'],
                shipping_tax=tax_detail['shipping_tax'],
                delivery_date=order_data.get('delivery_date'),
                subtotal=tax_detail['exempt'] + tax_detail['taxable'],
                total_price=total_price,
                payment_method=order_data['payment_method'],
                notes=order_data.get('notes', ''),
                billing_last_name=profile.last_name,
                billing_first_name=profile.first_name,
                billing_postal_code=profile.postal_code,
                billing_prefecture=profile.prefecture,
                billing_city=profile.city,
                billing_street_address=profile.street_address,
                billing_address_detail=profile.address_detail,
                billing_phone_number=profile.phone_number,
                shipping_last_name=(shipping.last_name if shipping else profile.last_name),
                shipping_first_name=(shipping.first_name if shipping else profile.first_name),
                shipping_postal_code=(shipping.postal_code if shipping else profile.postal_code),
                shipping_prefecture=(shipping.prefecture if shipping else profile.prefecture),
                shipping_city=(shipping.city if shipping else profile.city),
                shipping_street_address=(shipping.street_address if shipping else profile.street_address),
                shipping_address_detail=(shipping.address_detail if shipping else profile.address_detail),
                shipping_phone_number=(shipping.phone_number if shipping else profile.phone_number),
            )

            for item in cart_items:
                product = item.product

                # 在庫チェック
                if product.stock < item.quantity:
                    raise ValueError(f"{product.get_display_name()} の在庫が不足しています。（在庫: {product.stock}, 必要: {item.quantity}）")
                
                # 在庫減少
                product.stock -= item.quantity
                product.save()


                OrderItem.objects.create(
                    order=order,
                    product_name=item.product.get_display_name(),
                    product_price=item.product.total_price,
                    weight=item.product.weight,
                    quantity=item.quantity,
                    subtotal=item.subtotal,
                )
            cart_items.delete()

            # セッション破棄
            request.session.pop('order_data', None)
            request.session.pop('cart_ids', None)

            messages.success(request, "ご注文が確定しました。ありがとうございました！")
            return render(request, 'orders/order_complete.html', {'order': order})
    except Exception as e:
        messages.error(request, f"{e}:注文処理中にエラーが発生しました。恐れ入りますが、再度お試しください。")
        return redirect('orders:order_detail')
    
# マイページ表示用のご注文履歴
@login_required
def order_history(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-ordered_at')

    return render(request, 'orders/order_history.html', {
        'orders': orders
    })