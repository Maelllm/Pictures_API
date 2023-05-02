from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserImageViewSet, ImageUploadView, UserImageExpireViewSet, ExpirableSingleImageView

app_name = "api"

router = DefaultRouter()
router.register(r"images", UserImageViewSet)

expire_router = DefaultRouter()
expire_router.register(r'image', UserImageExpireViewSet, basename='expire')

urlpatterns = [
                  path("/", include(router.urls)),
                  path("upload/", ImageUploadView.as_view(), name="upload-image"),
                  path('expirable-links/', include(expire_router.urls)),
                  path("images/<int:pk>/expirable-link/<str:signed_value>.<str:expires_at>/",
                       ExpirableSingleImageView.as_view(),
                       name="expirable-image")
              ] + router.urls
