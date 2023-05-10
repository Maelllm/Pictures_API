from django.core.signing import Signer
from django.shortcuts import redirect
from django.urls import reverse

from images.models import UserImage


def expirable_image_view(request, signed_value):
    # Retrieve the UserImage object using the signed value
    signer = Signer()
    image_id = signer.unsign(signed_value)
    user_image = UserImage.objects.get(id=image_id)

    # Generate the expirable link using the expirable_link field
    expirable_url = user_image.expirable_link

    # Redirect to the expirable link
    return redirect(expirable_url)
