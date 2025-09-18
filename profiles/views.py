from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.urls import reverse
from .models import UserProfile,ShippingAddress 
from .forms import UserProfileForm, ShippingAddressForm

# Create your views here.
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    shipping, _ = ShippingAddress.objects.get_or_create(user=request.user)

    is_profile_registered = bool(profile.postal_code and profile.last_name)
    is_shipping_registered = bool(shipping.postal_code and shipping.last_name)

    return render(request, 'profiles/view_profile.html', {
        'profile': profile,
        'shipping': shipping,
        'is_profile_registered': is_profile_registered,
        'is_shipping_registered': is_shipping_registered,
    })


# @login_required
# def edit_profile(request, target):
#     next_url = request.GET.get('next') or request.POST.get('next')
#     is_order_flow = next_url and 'order' in next_url
    
#     # どちらのURLからリクエストが来たかを確認
#     if target == 'profile':
#         instance, _ = UserProfile.objects.get_or_create(user=request.user)
#         form_class = UserProfileForm
#         title = '基本住所（請求先）'
#     elif target == 'shipping':
#         instance, _ = ShippingAddress.objects.get_or_create(user=request.user)
#         form_class = ShippingAddressForm
#         title = '配送先住所'
#     else:
#         return redirect('profiles:view_profile')


@login_required
def edit_profile(request, target):
    next_url = request.GET.get('next') or request.POST.get('next')  # POST時も対応
    if not next_url:
        next_url = reverse('profiles:view_profile')
    is_order_flow = next_url and 'order' in next_url  # 最初に定義する！

    if target == 'profile':
        instance, _ = UserProfile.objects.get_or_create(user=request.user)
        form_class = UserProfileForm
        title = '基本住所（請求先）'
    elif target == 'shipping':
        instance, _ = ShippingAddress.objects.get_or_create(user=request.user)
        form_class = ShippingAddressForm
        title = '配送先住所'
    else:
        return redirect('profiles:view_profile')  
        # is_order_flowが未定義になる前に return しないようにするならここをあとに回す手もある

    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(next_url) if next_url else redirect('profiles:view_profile')
    else:
        form = form_class(instance=instance)

    return render(request, 'profiles/edit_profile.html', {
        'form': form,
        'title': title,
        'next_url': next_url,
        'is_order_flow': is_order_flow,
        'target': target,
    })
