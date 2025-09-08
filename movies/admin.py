from django.contrib import admin
from .models import Movie, Review, Order, OrderItem

admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
