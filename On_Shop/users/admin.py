from django.contrib import admin
from .models import UserProfile, Category, Product, Order, OrderItem, ShippingAddress

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'slug')  
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}  

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'complete', 'transaction_id')
    list_filter = ('complete', 'created_at')
    search_fields = ('user__username', 'transaction_id')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'address', 'city', 'state', 'zip_code', 'created_at')
    search_fields = ('address', 'city', 'state', 'zip_code')
