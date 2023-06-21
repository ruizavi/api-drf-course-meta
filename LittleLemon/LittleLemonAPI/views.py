from django.shortcuts import render
from django.contrib.auth.models import Group, User
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from rest_framework import generics
from rest_framework.response import Response
from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer

# Create your views here.


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name="Manager").exists()
        if gr or isAdmin:
            return [IsAuthenticated()]

        raise PermissionDenied()


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name="Manager").exists()
        if gr or isAdmin:
            return [IsAuthenticated()]

        raise PermissionDenied()


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name="Manager").exists()
        if gr or isAdmin:
            return [IsAuthenticated()]

        if self.request.method == "GET":
            return []

        raise PermissionDenied()


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        isAdmin = self.request.user.is_superuser
        gr = self.request.user.groups.filter(name="Manager").exists()
        if gr or isAdmin:
            return [IsAuthenticated()]

        if self.request.method == "GET":
            return []

        raise PermissionDenied()


class ManagersView(generics.ListAPIView):
    queryset = User.objects.all().filter(groups__name="Manager")
    serializer_class = UserSerializer

    def post(self, request):
        username = self.request.POST.get("username")

        if not username:
            raise ValidationError("Username field is required")
        
        user = self.queryset.get(username=username)

        group = Group.objects.get(name="Manager")

        user.groups.add(group)

        return Response(
            {"detail": f"User {username} add to Manager's group"}, status=200
        )

    def get_permissions(self):
        gr = self.request.user.groups.filter(name="Manager").exists()
        isAdmin = self.request.user.is_superuser
        if gr or isAdmin:
            return [IsAuthenticated()]

        raise PermissionDenied()


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
        gr = self.request.user.groups.filter(name="Manager").exists()
        isAdmin = self.request.user.is_superuser
        if gr or isAdmin:
            return [IsAuthenticated()]

        raise PermissionDenied()
