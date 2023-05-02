from rest_framework import serializers
from images.models import UserImage


# class UserImageSerializer(serializers.ModelSerializer):
#     image_url = serializers.SerializerMethodField()
#     thumbnail_200_url = serializers.SerializerMethodField()
#     thumbnail_400_url = serializers.SerializerMethodField()
#
#     def get_image_url(self, obj):
#         request = self.context.get("request")
#         if obj.image:
#             return request.build_absolute_uri(obj.image.url)
#         return None
#
#     def get_thumbnail_200_url(self, obj):
#         request = self.context.get("request")
#         if obj.thumbnail_200:
#             return request.build_absolute_uri(obj.thumbnail_200.url)
#         return None
#
#     def get_thumbnail_400_url(self, obj):
#         request = self.context.get("request")
#         if obj.thumbnail_400:
#             return request.build_absolute_uri(obj.thumbnail_400.url)
#         return None
#
#     class Meta:
#         model = UserImage
#         fields = ("image_url", "thumbnail_200_url", "thumbnail_400_url")
#
#
class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ("image",)


class ExpireImageSerializer(serializers.ModelSerializer):
    expirable_link = serializers.CharField()

    class Meta:
        model = UserImage
        fields = ['id', 'image', 'expirable_link']


class BaseUserImageSerializer(serializers.ModelSerializer):
    thumbnail_200_url = serializers.SerializerMethodField()

    def get_thumbnail_200_url(self, obj):
        request = self.context.get("request")
        if obj.thumbnail_200:
            return request.build_absolute_uri(obj.thumbnail_200.url)
        return None

    class Meta:
        model = UserImage
        fields = ("thumbnail_200_url",)


class AdvancedUserImageSerializer(BaseUserImageSerializer):
    thumbnail_400_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    def get_thumbnail_400_url(self, obj):
        request = self.context.get("request")
        if obj.thumbnail_400:
            return request.build_absolute_uri(obj.thumbnail_400.url)
        return None

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = UserImage
        fields = ("thumbnail_200_url", "thumbnail_400_url", "image_url")


class SingleImageSerializer(serializers.ModelSerializer):
    expirable_link = serializers.SerializerMethodField()

    class Meta:
        model = UserImage
        fields = ['id', 'created_at', 'expirable_link']

    def get_expirable_link(self, obj):
        request = self.context.get('request')
        if request is None:
            return None

        return obj.image.url

