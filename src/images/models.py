import sys
from io import BytesIO

from django.core.files.uploadedfile import (InMemoryUploadedFile,
                                            TemporaryUploadedFile)
from django.db import models
from PIL import Image as PImage


class UserImage(models.Model):
    image = models.ImageField(upload_to="media/images/")
    thumbnail_200 = models.ImageField(upload_to="media/thumbnails_200", blank=True, null=True)
    thumbnail_400 = models.ImageField(upload_to="media/thumbnails_400", blank=True, null=True)
    creation_date = models.DateField(auto_now_add=True)

    # TODO userfield

    def thumb_name(self, height, format):
        return self.image.name.split(".")[0] + "_thumbnail_" + str(height) + "." + format.lower()

    def thumbnail_creation(self, new_height: int, new_format: str):
        img = PImage.open(self.image)
        width, height = img.size
        ratio = height / width
        new_width = int(new_height / ratio)
        img.thumbnail((new_width, new_height))
        thumb_io = BytesIO()

        try:
            img.save(thumb_io, format=new_format)
        except KeyError as e:
            raise ValueError(f"Invalid format: {new_format}") from e
        except Exception as e:
            print(f"Thumbnail creation failed: {e}")
            return None

        thumbnail = InMemoryUploadedFile(
            thumb_io,
            None,
            self.thumb_name(new_height, new_format),
            f"image/{new_format}",
            sys.getsizeof(thumb_io),
            None,
        )
        return thumbnail

    def save(self, *args, **kwargs):
        if self.image and not self.thumbnail_200:
            if self.image.name.lower().endswith((".jpg", ".jpeg")):
                self.thumbnail_200.save(self.thumb_name(200, "JPEG"), self.thumbnail_creation(200, "JPEG"), save=False)
            elif self.image.name.lower().endswith(".png"):
                self.thumbnail_200.save(self.thumb_name(200, "PNG"), self.thumbnail_creation(200, "PNG"), save=False)
        if self.image and not self.thumbnail_400:
            if self.image.name.lower().endswith((".jpg", ".jpeg")):
                self.thumbnail_400.save(self.thumb_name(400, "JPEG"), self.thumbnail_creation(400, "JPEG"), save=False)
            elif self.image.name.lower().endswith(".png"):
                self.thumbnail_400.save(self.thumb_name(400, "PNG"), self.thumbnail_creation(400, "PNG"), save=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.thumbnail_200:
            self.thumbnail_200.delete(save=False)
        if self.thumbnail_400:
            self.thumbnail_400.delete(save=False)
        if self.image:
            self.image.delete(save=False)

        super().delete(*args, **kwargs)
