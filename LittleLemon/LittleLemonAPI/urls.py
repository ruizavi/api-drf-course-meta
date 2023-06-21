from django.urls import path
from .views import (
    CategoriesView,
    SingleCategoryView,
    MenuItemsView,
    SingleMenuItemView,
    ManagersView,
    SingleManagerView,
    DeliveryCrewView,
    SingleDeliveryView
)

urlpatterns = [
    path("category/", CategoriesView.as_view()),
    path("category/<int:pk>/", SingleCategoryView.as_view()),
    path("menu-items/", MenuItemsView.as_view()),
    path("menu-items/<int:pk>/", SingleMenuItemView.as_view()),
    path("groups/managers/users/", ManagersView.as_view()),
    path("groups/managers/users/<int:pk>/", SingleManagerView.as_view()),
    path("groups/delivery-crew/users/", DeliveryCrewView.as_view()),
    path("groups/delivery-crew/users/<int:pk>/", SingleDeliveryView.as_view()),
]
