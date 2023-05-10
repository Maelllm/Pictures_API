from django import forms
from django.contrib import admin

from images.models import UserImage


class UserImageAdmin(admin.ModelAdmin):
    list_display = ["id", "image", "thumbnail_200", "thumbnail_400", "creation_date"]
    readonly_fields = ["thumbnail_200", "thumbnail_400"]


admin.site.register(UserImage, UserImageAdmin)
