from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import logout_view

urlpatterns = [
    # Authentication/Login
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Storefront
    path('', views.product_list, name='product_list'),  # Homepage
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart and Checkout
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),

    # Orders & Confirmation
    path('my-orders/', views.my_orders, name='my_orders'),
    path('confirm-whatsapp/<int:order_id>/', views.whatsapp_confirm, name='whatsapp_confirm'),
    path('thank-you/<int:order_id>/', views.thank_you, name='thank_you'),

    #iNVOICE
    path('invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),


    #Webhook
    path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
]
