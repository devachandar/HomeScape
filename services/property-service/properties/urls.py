from django.urls import path

from . import views

urlpatterns = [
    path("", views.PropertyListCreateView.as_view()),
    path("seller/mine", views.SellerMinePropertiesView.as_view()),
    path("me/favorites", views.MyFavoritesView.as_view()),
    path("<str:pk>", views.PropertyDetailView.as_view()),
    path("<str:pk>/favorite", views.FavoriteView.as_view()),
]
