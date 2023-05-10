import time
from datetime import datetime, timedelta

from django.core.signing import (BadSignature, SignatureExpired, Signer,
                                 TimestampSigner)
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView, View
from rest_framework.viewsets import ModelViewSet

from api.serializer import (AdvancedUserImageSerializer,
                            BaseUserImageSerializer, ExpireImageSerializer,
                            ImageUploadSerializer, SingleImageSerializer)
from images.models import UserImage


class UserImageViewSet(ModelViewSet):
    queryset = UserImage.objects.all()
    serializer_class = BaseUserImageSerializer

    def get_serializer_class(self):
        user = self.request.user
        user_type = getattr(user, "user_type", None)

        if user.is_authenticated:
            if user_type == 1:
                return BaseUserImageSerializer
            elif user_type in [2, 3, 4]:
                return AdvancedUserImageSerializer
        else:
            raise PermissionDenied("Please authorize yourself.")


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data["image"]
            user_image = UserImage(image=image)
            user_image.save()
            return Response({"message": "Image uploaded successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserImageExpireViewSet(viewsets.ViewSet):
    DEFAULT_EXPIRATION_TIME = 300  # seconds

    def retrieve(self, request, pk=None):
        """
        Retrieve an expirable link for a user image.
        """
        image = get_object_or_404(UserImage, pk=pk)
        expirable_link = self.get_expirable_link(request, pk=pk)
        serializer = ExpireImageSerializer({"id": image.id, "image": image.image, "expirable_link": expirable_link})
        return Response(serializer.data)

    def get_expirable_link(self, request, pk, expires_in=None):
        if expires_in is None:
            expires_in = self.DEFAULT_EXPIRATION_TIME

        try:
            expires_in = int(expires_in)
        except ValueError:
            expires_in = self.DEFAULT_EXPIRATION_TIME

        signer = TimestampSigner()
        signed_value = signer.sign(str(pk))
        expiration_time = datetime.now() + timedelta(seconds=expires_in)
        utc_expiration_time = timezone.make_aware(expiration_time, timezone.utc)
        expirable_link = request.build_absolute_uri(
            f"/api/images/{pk}/expirable-link/{signed_value}.{int(utc_expiration_time.timestamp())}"
        )

        return expirable_link

    @action(detail=True, methods=["get"])
    def expire(self, request, pk=None):
        """
        Endpoint to generate and return a newly generated expiring link for the UserImage.
        """
        image = get_object_or_404(UserImage, pk=pk)
        expirable_link = self.get_expirable_link(request, pk)
        serializer = ExpireImageSerializer({"id": image.id, "image": image.image, "expirable_link": expirable_link})
        return Response(serializer.data)


class ExpirableSingleImageView(View):
    def get(self, request, pk, signed_value, expires_at):
        # Parse the expires_at timestamp
        try:
            expires_at = float(expires_at)
            expires_dt = datetime.fromtimestamp(expires_at, tz=timezone.utc)
        except ValueError:
            return HttpResponseNotFound("Invalid timestamp")

        # Check if the link has expired
        now = timezone.now()
        print(now, expires_dt)
        if now > expires_dt:
            return HttpResponseNotFound("Link has expired")

        # Verify the signed value using the TimestampSigner
        signer = TimestampSigner()
        try:
            pk_str = signer.unsign(signed_value, max_age=expires_at - now.timestamp())
            pk = int(pk_str)
        except BadSignature:
            return HttpResponseNotFound("Invalid signature")
        except ValueError:
            return HttpResponseNotFound("Invalid signed value")

        # Look up the UserImage
        try:
            image = UserImage.objects.get(pk=pk)
        except UserImage.DoesNotExist:
            return HttpResponseNotFound("Image not found")

        # Return the image data
        with image.image.open() as f:
            return HttpResponse(
                f.read(),
                content_type=image.image.file.content_type
                if hasattr(image.image.file, "content_type")
                else "application/octet-stream",
            )
