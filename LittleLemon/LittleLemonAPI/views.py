from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer
# Create your views here.


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (not gr):
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (not gr):
            raise PermissionDenied()

        return [IsAuthenticated()]


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        print('Aqui pasa post')
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (not gr):
            raise PermissionDenied()

        return [IsAuthenticated()]


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if (self.request.method == 'GET'):
            return []
        print('Aqui pasa post')
        gr = self.request.user.groups.filter(name='Manager').exists()
        if (not gr):
            raise PermissionDenied()

        return [IsAuthenticated()]
