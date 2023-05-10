import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from images.models import UserImage
from images.utils import create_simple_image


class UserImageViewSetTest(APITestCase):
    def setUp(self):
        # Create both png and jpeg images
        jpeg_image = create_simple_image(format="JPEG", content_type="image/jpeg", height=300, width=300)
        png_image = create_simple_image(format="PNG", content_type="image/png", height=300, width=300)
        self.jpeg_user_image = UserImage.objects.create(image=jpeg_image)
        self.png_user_image = UserImage.objects.create(image=png_image)

    def tearDown(self):
        self.jpeg_user_image.delete()
        self.png_user_image.delete()

    def test_not_authorize(self):
        url = reverse("api:images-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_get_authenticated_user_with_user_type_1(self):
        # Create a user with user_type 1 and authenticate
        user = get_user_model().objects.create_user(email="testuser@test.com", password="testpassword")
        user.user_type = 1
        user.save()
        self.client.force_authenticate(user=user)

        url = reverse("api:images-list")
        response = self.client.get(url)

        # Check the status code
        self.assertEqual(response.status_code, 200)

        # Check the fields accessible to user_type 1
        expected_fields = ["thumbnail_200_url"]
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIsInstance(response.data[0], dict)
            for field in expected_fields:
                self.assertIn(field, response.data[0])
            self.assertNotIn("thumbnail_400_url", response.data[0])
            self.assertNotIn("image_url", response.data[0])

    def test_get_authenticated_user_with_user_type_not_1(self):
        # Create a user with user_type 1 and authenticate
        user = get_user_model().objects.create_user(email="testuser@test.com", password="testpassword")
        user.user_type = 2
        user.save()
        self.client.force_authenticate(user=user)

        url = reverse("api:images-list")
        response = self.client.get(url)

        # Check the status code
        self.assertEqual(response.status_code, 200)

        # Check the fields accessible to user_type 1
        expected_fields = ["thumbnail_200_url", "thumbnail_400_url", "image_url"]
        self.assertIsInstance(response.data, list)
        if response.data:
            self.assertIsInstance(response.data[0], dict)
            for field in expected_fields:
                self.assertIn(field, response.data[0])


class ImageUploadViewTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(email="testuser@test.com", password="testpassword")
        user.user_type = 1
        user.save()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        media_path = os.path.join(settings.MEDIA_ROOT, "media")

        # Recursively traverse the media folder
        for root, dirs, files in os.walk(media_path):
            for filename in files:
                if filename.startswith("test_image"):
                    file_path = os.path.join(root, filename)
                    os.remove(file_path)

    def test_image_upload_success(self):
        # Create a valid image file for upload
        image_file = create_simple_image()

        # Make a POST request to the endpoint
        url = reverse("api:upload-image")
        response = self.client.post(url, {"image": image_file}, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Image uploaded successfully")

    def test_image_upload_not_image(self):
        # Create an invalid image file for upload (e.g., a text file)
        image_file = SimpleUploadedFile("test_image.txt", b"text_content", content_type="text/plain")

        # Make a POST request to the endpoint
        url = reverse("api:upload-image")
        response = self.client.post(url, {"image": image_file}, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "image", response.data
        )  # Assuming the serializer provides an error message for the "image" field
        self.assertEqual(
            response.data["image"][0],
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
        )

    def test_image_upload_invalid_image(self):
        # Create a BMP image file for upload
        image_file = create_simple_image(format="BMP", content_type="image/bmp", height=100, width=100)

        # Make a POST request to the endpoint
        url = reverse("api:upload-image")
        response = self.client.post(url, {"image": image_file}, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data)
        self.assertEqual(
            response.data["image"][0],
            "Invalid image format. Only JPEG and PNG are supported.",
        )
