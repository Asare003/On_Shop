from .models import Order

def cart_items_count(request):
    count = 0
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, complete=False).first()
        if order:
            count = sum(item.quantity for item in order.items.all())
    return {'cart_items_count': count}
