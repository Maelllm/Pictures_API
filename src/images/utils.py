from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def create_simple_image(format="JPEG", content_type="image/jpeg", height=100, width=100):
    image = Image.new("RGB", (width, height))
    image_io = BytesIO()
    image.save(image_io, format=format)
    image_file = SimpleUploadedFile(f"test_image.{format.lower()}", image_io.getvalue(), content_type=content_type)
    return image_file
