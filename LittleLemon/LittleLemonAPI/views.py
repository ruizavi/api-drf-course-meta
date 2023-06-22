from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework import generics
from rest_framework.response import Response
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, SimpleOrderSerializer
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class PaginationClass(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 6


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'title']
    search_fields = ['title', 'category__title']
    filterset_fields = ['category']
    pagination_class = PaginationClass

    def get_permissions(self):
        if self.request.method == "GET":
            return []

        isManager = self.request.user.groups.filter(name="Manager").exists()
        if not isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []

        isManager = self.request.user.groups.filter(name="Manager").exists()
        if not isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class ManagersView(generics.ListAPIView):
    queryset = User.objects.all().filter(groups__name="Manager")
    serializer_class = UserSerializer

    def post(self, request):
        user_id = int(self.request.POST.get("user_id"))

        if not user_id:
            raise ValidationError("Username field is required")

        user = User.objects.filter(id=user_id).first()
        print(user)

        if not user:
            raise ValidationError(detail="User not found")

        group = Group.objects.get(name="Manager")

        user.groups.add(group)

        return Response(
            {"detail": f"User {user_id} add to Manager's group"}, status=200
        )

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if not isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleManagerView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer

    def get(self, request, pk):
        user = User.objects.get(id=pk)

        if not user or not user.groups.filter(name="Manager"):
            raise NotFound()

        serializer = self.serializer_class(user)

        return Response(serializer.data)

    def delete(self, request, pk):
        group = Group.objects.get(name="Manager")

        user = User.objects.get(id=pk)

        if not user:
            raise NotFound()

        user.groups.remove(group)

        return Response({"detail": f"User remove to Manager's group"}, status=200)

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if not isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class DeliveryCrewView(generics.ListAPIView):
    queryset = User.objects.all().filter(groups__name="delivery crew")
    serializer_class = UserSerializer

    def post(self, request):
        user_id = int(self.request.POST.get("user_id"))

        if not user_id:
            raise ValidationError("Username field is required")

        user = User.objects.filter(id=user_id).first()
        print(user)

        if not user:
            raise ValidationError(detail="User not found")
        group = Group.objects.get(name="delivery crew")

        user.groups.add(group)

        return Response(
            {"detail": f"User {user_id} add to delivery crew group"}, status=200
        )

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if not isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleDeliveryView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer

    def get(self, request, pk):
        user = User.objects.get(id=pk)

        if not user or not user.groups.filter(name="delivery crew"):
            raise NotFound()

        serializer = self.serializer_class(user)

        return Response(serializer.data)

    def delete(self, request, pk):
        group = Group.objects.get(name="delivery crew")

        user = User.objects.get(id=pk)

        if not user:
            raise NotFound()

        user.groups.remove(group)

        return Response({"detail": f"User remove to delivery crew group"}, status=200)

    def get_permissions(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        if isManager:
            raise PermissionDenied()

        return [IsAuthenticated()]


class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request):

        Cart.objects.filter(user=self.request.user).delete()

        return Response({'detail': 'Ok'}, status=200)


class OrderView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    pagination_class = PaginationClass
    ordering_fields = ['total', 'status', 'date']
    search_fields = ['orders__menuitem__title']

    def get_queryset(self):
        isManager = self.request.user.groups.filter(name="Manager").exists()
        isDeliveryCrew = self.request.user.groups.filter(
            name="Manager").exists()
        if isManager:
            return Order.objects.all()

        if isDeliveryCrew:
            return Order.objects.filter(delivery_crew=self.request.user)

        return Order.objects.filter(user=self.request.user)


class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = SimpleOrderSerializer

    def delete(self, request, pk):
        isManager = self.request.user.groups.filter(name="Manager").exists()

        if not isManager:
            raise PermissionDenied()

        order = Order.objects.filter(id=pk).first()

        order.delete()

        return Response({'detail': 'Order deleted successfully'}, status=200)
