from django.test import TestCase
from PIL import Image

from images.models import UserImage
from images.utils import create_simple_image


class UserImageModelTest(TestCase):
    def setUp(self):
        # Create both png and jpeg images
        jpeg_image = create_simple_image(format="JPEG", content_type="image/jpeg", height=300, width=300)
        png_image = create_simple_image(format="PNG", content_type="image/png", height=300, width=300)
        self.jpeg_user_image = UserImage.objects.create(image=jpeg_image)
        self.png_user_image = UserImage.objects.create(image=png_image)

    def tearDown(self):
        self.jpeg_user_image.delete()
        self.png_user_image.delete()

    def test_save_image_and_generate_thumbnails(self):
        self.jpeg_user_image.save()
        self.png_user_image.save()

        # Check the thumbnail images are created and saved correctly
        self.assertTrue(self.jpeg_user_image.thumbnail_200)
        self.assertTrue(self.jpeg_user_image.thumbnail_400)
        self.assertTrue(self.png_user_image.thumbnail_200)
        self.assertTrue(self.png_user_image.thumbnail_400)

    def test_thumbnail_resolution(self):
        image_file = create_simple_image(format="JPEG", height=600, width=300)
        user_image = UserImage.objects.create(image=image_file)

        try:
            # Check the resolution of the thumbnail
            thumbnail_200 = user_image.thumbnail_200
            thumbnail_200.open()
            thumbnail_200_image = Image.open(thumbnail_200)
            self.assertEqual(thumbnail_200_image.size, (100, 200))
            thumbnail_400 = user_image.thumbnail_400
            thumbnail_400.open()
            thumbnail_400_image = Image.open(thumbnail_400)
            self.assertEqual(thumbnail_400_image.size, (200, 400))

        finally:
            user_image.delete()

    def test_thumb_name(self):
        # Check the thumbnail names for different heights and formats
        expected_names = {
            (1200, "JPEG"): "_thumbnail_1200.jpeg",
            (300, "JPEG"): "_thumbnail_300.jpeg",
            (500, "PNG"): "_thumbnail_500.png",
            (700, "PNG"): "_thumbnail_700.png",
        }
        for (height, format), expected_suffix in expected_names.items():
            thumb_name = self.jpeg_user_image.thumb_name(height, format)
            self.assertTrue(thumb_name.endswith(expected_suffix))

    def test_missing_image_file(self):
        # Create a UserImage instance without an image file
        user_image = UserImage.objects.create()

        # Assert that the thumbnail fields are not generated
        self.assertFalse(user_image.thumbnail_200)
        self.assertFalse(user_image.thumbnail_400)

        user_image.delete()

    def test_thumbnail_creation_error_handling(self):
        # Test with an invalid format
        with self.assertRaises(ValueError):
            self.jpeg_user_image.thumbnail_creation(200, "INVALID_FORMAT")

        # Test with an invalid height
        with self.assertRaises(ValueError):
            self.jpeg_user_image.thumbnail_creation(-100, "JPEG")
