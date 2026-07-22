import requests
from django.conf import settings

from . import mailer

AUTH_SERVICE_URL = settings.INTERNAL_SERVICE_URLS["auth"]


def _resolve_user_email(user_id):
    try:
        res = requests.get(f"{AUTH_SERVICE_URL}/internal/users/{user_id}", timeout=5)
        if res.status_code == 200:
            return res.json().get("email")
    except requests.RequestException:
        pass
    return None


def handle_user_registered(payload):
    mailer.send("welcome", payload["email"], {"fullName": payload["fullName"]})


def handle_property_created(payload):
    seller_email = _resolve_user_email(payload["seller_id"])
    if seller_email:
        mailer.send("listingLive", seller_email, {"title": payload["title"]})


def handle_inquiry_created(payload):
    seller_email = _resolve_user_email(payload.get("seller_id") or payload.get("sellerId"))
    if seller_email:
        mailer.send("newInquiry", seller_email, {"propertyTitle": payload.get("propertyTitle", "your listing")})


HANDLERS = {
    "UserRegistered": handle_user_registered,
    "PropertyCreated": handle_property_created,
    "InquiryCreated": handle_inquiry_created,
}
