from django.contrib import messages #フラッシュメッセージ
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CartItem
from products.models import Product
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

# ==================================
# 全て@login_requiredとする
# ==================================

# カート表示
@login_required
def cart_view(request): 
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        item.subtotal = item.product.total_price * item.quantity
        item.subtotal_with_tax = item.product.total_price_with_tax * item.quantity

    total_price = sum(item.subtotal for item in cart_items)
    total_price_with_tax = sum(item.subtotal_with_tax for item in cart_items)

    return render(request, 'cart/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_price_with_tax': total_price_with_tax,
    })

# カートに商品を追加
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # 在庫チェック（カートページにリダイレクト（エラーメッセージを表示）
    if product.stock < quantity:
        messages.error(request, f"申し訳ありませんが、{product.name} の在庫が不足しています。現在の在庫は{product.stock}個です。")
        return redirect('cart:view_cart')

    # すでにカートにあるか確認して追加 or 更新
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if created:
        cart_item.quantity = quantity  # 新規作成時に数量を反映
    else:
        cart_item.quantity += quantity  # 既存なら加算

    cart_item.save()

    # カートに追加後は元のページに戻る
    next_url = request.GET.get('next', '/')
    return redirect(next_url)

# カート内で商品を削除し、再度ページを表示する
@login_required
def remove_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)
    cart_item.delete()

    return redirect('cart:view_cart')

# カート内の商品の数量を更新
@login_required
def update_cart_item(request, cart_item_id):
    quantity = int(request.POST.get('quantity', 1))

    try:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user)  # カートの中身を取得
        product = cart_item.product  # 中身の商品情報を取得

        # 在庫チェック
        if product.stock < quantity:
            messages.error(request, f"申し訳ありませんが、{product.name} の在庫が不足しています。現在の在庫は{product.stock}個です。")
            return redirect('cart:view_cart')

        # 数量を更新
        cart_item.quantity = quantity
        cart_item.save()

    except CartItem.DoesNotExist:
        # 商品がカートに存在しない
        messages.error(request, "指定された商品はカートに存在しません。")
        return redirect('cart:view_cart')

    return redirect('cart:view_cart')


# 注文完了時にカート内の商品を削除する
@login_required
def complete_order(request):
    CartItem.objects.filter(user=request.user).delete()
    return render(request, 'orders/order_complete.html')

# カートのバッヂ
@login_required
def badge_partial(request):
    count = CartItem.objects.filter(user=request.user).aggregate(
        total=Coalesce(Sum('quantity'), 0)
    )['total'] or 0
    return render(request, 'cart/_badge.html', {'cart_count': count})