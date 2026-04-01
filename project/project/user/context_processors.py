from .models import Cart, Cartitems
from django.db.models import Sum

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            # Calculate total quantity of all items in cart
            total_quantity = Cartitems.objects.filter(cart=cart).aggregate(Sum('quantity'))['quantity__sum'] or 0
            return {'cart_count': total_quantity}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}
