from django.urls import path
from rest_framework.routers import DefaultRouter

from images.views import expirable_image_view

# urlpatterns = [
#     path('expirable/image/expirable/<str:signed_value>/', expirable_image_view, name='expirable_image_view'),
# ]
