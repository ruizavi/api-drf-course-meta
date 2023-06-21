from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound


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
    menuitem = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        read_only_fields = ('id', 'menuitem',
                            'price', 'unit_price', 'user')
        fields = ['id', 'menuitem', 'quantity',
                  'price', 'unit_price', 'user', 'menuitem_id']

    def save(self, **kwargs):
        menuitem_id = self.context['request'].data.get('menuitem_id')
        quantity = self.context['request'].data.get('quantity')

        product = MenuItem.objects.get(id=menuitem_id)
        if not product:
            raise NotFound()

        unit_price = getattr(product, 'price')

        kwargs['unit_price'] = unit_price
        kwargs['price'] = int(quantity) * unit_price
        kwargs['user'] = self.context['request'].user

        return super().save(**kwargs)
    # def calc_total(self):
    #     return self.unit_price * self.quantity
