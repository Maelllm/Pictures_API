from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (ExpirableSingleImageView, ImageUploadView,
                    UserImageExpireViewSet, UserImageViewSet)

app_name = "api"

router = DefaultRouter()
router.register(r"images", UserImageViewSet, basename="images")

expire_router = DefaultRouter()
expire_router.register(r"image", UserImageExpireViewSet, basename="expire")

urlpatterns = [
    path("/", include(router.urls)),
    path("upload/", ImageUploadView.as_view(), name="upload-image"),
    path("expirable-links/", include(expire_router.urls)),
    path(
        "images/<int:pk>/expirable-link/<str:signed_value>.<str:expires_at>/",
        ExpirableSingleImageView.as_view(),
        name="expirable-image",
    ),
] + router.urls
