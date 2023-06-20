from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
# Create your views here.


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (gr or isAdmin):
            return [IsAuthenticated()]

        raise PermissionDenied()


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (gr or isAdmin):
            return [IsAuthenticated()]

        raise PermissionDenied()


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (gr or isAdmin):
            return [IsAuthenticated()]

        if (self.request.method == 'GET'):
            return []

        raise PermissionDenied()


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (gr or isAdmin):
            return [IsAuthenticated()]

        if (self.request.method == 'GET'):
            return []

        raise PermissionDenied()
