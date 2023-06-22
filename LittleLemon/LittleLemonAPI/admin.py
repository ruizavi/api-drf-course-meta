from django.contrib import admin
from .models import OrderItem, Order, MenuItem, Category, Cart
# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Cart)
