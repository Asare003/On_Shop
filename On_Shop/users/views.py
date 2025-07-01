from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Product, Category, Order, OrderItem, ShippingAddress
from .forms import CustomUserCreationForm

import uuid

# Show all products
def product_list(request):
    categories = Category.objects.all()
    products_by_category = {
        cat.slug: Product.objects.filter(category=cat)[:8]  # Show top 8 per category
        for cat in categories
    }
    return render(request, 'users/product_list.html', {
        'categories': categories,
        'products_by_category': products_by_category
    })

# Logout
def logout_view(request):
    logout(request)
    return redirect('/')

# Show one product
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'users/product_detail.html', {'product': product})

# Registration without OTP
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Ensure you only use an incomplete order
    order, created = Order.objects.get_or_create(user=request.user, complete=False)

    order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            messages.warning(request, "Invalid quantity selected.")
            return redirect('product_detail', slug=product.slug)

        if item_created:
            order_item.quantity = quantity
        else:
            order_item.quantity += quantity

        order_item.save()
        messages.success(request, f"{product.name} added to cart.")

    return redirect('cart')

# View cart
@login_required
def cart_view(request):
    order = Order.objects.filter(user=request.user, complete=False).first()
    if not order:
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')

    items = order.items.all()
    total = order.get_total
    return render(request, 'users/cart.html', {
        'cart_items': items,
        'cart_total': total
    })

# Update cart item
@require_POST
@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    new_quantity = int(request.POST.get('quantity', 1))

    if new_quantity <= 0:
        item.delete()
        messages.info(request, f"{item.product.name} removed from cart.")
    else:
        item.quantity = new_quantity
        item.save()
        messages.success(request, f"{item.product.name} updated to {new_quantity}.")

    return redirect('cart')

# Clear cart
@require_POST
@login_required
def clear_cart(request):
    order = Order.objects.filter(user=request.user, complete=False).first()
    if order:
        order.items.all().delete()
        messages.info(request, "Your cart has been cleared.")
    return redirect('cart')

# Checkout
from django.core.mail import send_mail
from django.conf import settings

@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, complete=False).first()

    if not order:
        messages.warning(request, "No active order to checkout.")
        return redirect('cart')

    if not order.transaction_id or Order.objects.filter(transaction_id=order.transaction_id, complete=True).exists():
        order.transaction_id = f"ONSHOP-{uuid.uuid4()}"
        order.save()

    if request.method == 'POST':
        ShippingAddress.objects.create(
            user=request.user,
            order=order,
            address=request.POST['address'],
            city=request.POST['city'],
            state=request.POST['state'],
            zip_code=request.POST['zip_code'],
            created_at=timezone.now()
        )

        order.transaction_id = f"ONSHOP-{uuid.uuid4()}"
        order.save()

        try:
            send_mail(
                subject="Order Confirmation - OnShop",
                message=f"Thanks for your order #{order.id}!\nTotal: GHS {order.get_total()}\nWe’ll process it soon.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print("Email sending failed:", e)

        messages.success(request, "Shipping details saved. Confirmation sent to email. Now complete payment.")
        return redirect('checkout')

    return render(request, 'users/checkout.html', {'order': order})

# View past orders
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, complete=True).order_by('-created_at')
    return render(request, 'users/my_orders.html', {'orders': orders})

# WhatsApp order confirmation
@login_required
def whatsapp_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    phone_number = "233592377833"

    message = (
        f"Hi, I just placed Order #{order.id}.\n"
        f"Total: ${order.get_total:.2f}\n"
        f"Name: {request.user.username}"
    )

    whatsapp_url = f"https://wa.me/{phone_number}?text={message.replace(' ', '%20').replace('\n', '%0A')}"
    order.complete = True
    order.save()
    return redirect(whatsapp_url)

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Thank You Page
@login_required
def thank_you(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.complete:
        order.complete = True
        order.save()

    return render(request, 'users/thank_you.html', {'order': order})

# Download Invoice as PDF
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = list(order.items.all())
    shipping = ShippingAddress.objects.filter(order=order).first()

    template = get_template("users/invoice.html")
    html = template.render({
        "order": order,
        "items": items,
        "shipping": shipping
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def paystack_webhook(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        event = payload.get('event')

        if event == 'charge.success':
            data = payload.get('data', {})
            ref = data.get('reference')
            amount_paid = int(data.get('amount', 0)) / 100

            try:
                order = Order.objects.get(transaction_id=ref, complete=False)
                if round(order.get_total(), 2) == round(amount_paid, 2):
                    order.complete = True
                    order.save()
            except Order.DoesNotExist:
                pass

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'status': 'received'}, status=200)
