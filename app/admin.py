from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, CartItem
from .models import Brand

admin.site.register(Brand)

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# Product Admin (ONLY ONE)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','brand', 'category', 'price', 'discount', 'discounted_price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('price', 'discount', 'stock')
    ordering = ('name',)
    inlines = [ProductImageInline]

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'total', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'phone')

# OrderItem Admin
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order', 'product')

# CartItem Admin
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('user', 'product')