from django.urls import path, include
from . import views
from django.urls import re_path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),
    path("movies/<int:pk>/review/", views.review_create, name="review_create"),

    # Authentication URLs (login, logout, password change/reset)
    path("accounts/", include("django.contrib.auth.urls")),

    # Registration
    path("accounts/register/", views.register, name="register"),

    #cart
    path("cart/", views.view_cart, name="view_cart"),
    path("add_to_cart/<int:movie_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove_from_cart/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("place_order/", views.place_order, name="place_order"),
    path("orders/", views.view_orders, name="view_orders"),

    # Review URLs
    path("review/<int:review_id>/edit/", views.review_edit, name="review_edit"),
    path("review/<int:review_id>/delete/", views.review_delete, name="review_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)