from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("email", "id")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title")


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ("id", "title", "price", "featured",
                  "category_id", "category")


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer
    user = UserSerializer
    unit_price = menuitem.get_value('price')
    price = serializers.SerializerMethodField(method_name='calc_total')

    class Meta:
        model = Cart
        fields = ('id', 'menuitem', 'quantity', 'unit_price', 'price', 'user')

    def calc_total(self, cart: Cart):
        return self.unit_price * cart.unit_price
