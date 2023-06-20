from django.urls import path
from .views import CategoriesView, SingleCategoryView, MenuItemsView, SingleMenuItemView

urlpatterns = [
    path('category/', CategoriesView.as_view()),
    path('category/<int:pk>/', SingleCategoryView.as_view()),
    path('menu-items/', MenuItemsView.as_view()),
    path('menu-items/<int:pk>', SingleMenuItemView.as_view())
]
