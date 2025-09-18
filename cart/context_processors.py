from django.db.models import Sum
from django.db.models.functions import Coalesce
from .models import CartItem

# ログインユーザーのカート内の商品数量の合計をテンプレートに渡す
def cart_badge(request):
    if not request.user.is_authenticated:
        return {'cart_count': 0}
    count = CartItem.objects.filter(user=request.user).aggregate(
        total=Coalesce(Sum('quantity'), 0)
    )['total'] or 0
    return {'cart_count': count}
