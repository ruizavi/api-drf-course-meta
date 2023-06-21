from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError, ErrorDetail


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

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise NotFound(detail="Category not exists")
        return value


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer
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

        product = MenuItem.objects.filter(id=menuitem_id).first()
        if not product:
            raise NotFound(detail='Item not exists')

        cart_product = Cart.objects.filter(menuitem=product)
        if cart_product:
            raise ValidationError(
                detail='There is already an item in the cart with that product')

        unit_price = getattr(product, 'price')

        kwargs['unit_price'] = unit_price
        kwargs['price'] = int(quantity) * unit_price
        kwargs['user'] = self.context['request'].user

        return super().save(**kwargs)
    # def calc_total(self):
    #     return self.unit_price * self.quantity


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer

    class Meta:
        model = Order
        read_only_fields = ('user', 'total', 'status', 'delivery_crew')
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

    def save(self, **kwargs):
        user = self.context['request'].user
        kwargs['user'] = user

        cart_items = Cart.objects.all().filter(user=user)

        if len(cart_items) == 0:
            raise ValidationError(detail='Cart is empty')

        total = sum(getattr(item, 'price') for item in cart_items)
        kwargs['total'] = total

        ord = super().save(**kwargs)

        for i in cart_items:
            new_order = {'order': ord.id, 'menuitem': getattr(
                i, 'menuitem_id'), 'quantity': getattr(i, 'quantity'), 'unit_price': getattr(i, 'unit_price'), 'price': getattr(i, 'price')}

            order_item = OrderItemSerializer(data=new_order)
            order_item.is_valid(raise_exception=True)
            order_item.save()

        cart_items.delete()

        return ord


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer

    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity',
                  'unit_price', 'price']
