from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", 'user_id')
        read_only_fields = ("email", "id", "username")


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


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity',
                  'unit_price', 'price']


class SimpleOrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    delivery_crew = serializers.StringRelatedField()
    orders = OrderItemSerializer(read_only=True, many=True)
    status = serializers.BooleanField()
    delivery_crew_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        read_only_fields = ('user', 'total', 'status',
                            'delivery_crew', 'orders', 'date')
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'total', 'date', 'orders', 'delivery_crew_id']

    def update(self, instance, validated_data):
        user = self.context["request"].user

        is_Delivery = user.groups.filter(name="delivery crew").first()
        if is_Delivery and self.context['request'].method == "PATCH":
            validated_data.pop('delivery_crew_id')
            return super().update(instance, validated_data)

        is_Manager = user.groups.filter(name="Manager").first()
        if not is_Manager:
            raise PermissionDenied()

        delivery_selected = User.objects.filter(
            id=self.context['request'].data['delivery_crew_id'])

        if not delivery_selected.exists():
            raise ValidationError("This user is not delivery crew")

        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    orders = OrderItemSerializer(read_only=True, many=True)
    delivery = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Order
        read_only_fields = ('user', 'total', 'status',
                            'delivery_crew', 'orders')
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'total', 'date', 'orders', 'delivery']
