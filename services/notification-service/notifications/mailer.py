import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

TEMPLATES = {
    "welcome": lambda ctx: (
        "Welcome to HomeScape",
        f"Hi {ctx['fullName']}, welcome to HomeScape! Start browsing homes or list your first property.",
    ),
    "newInquiry": lambda ctx: (
        f'New inquiry on "{ctx["propertyTitle"]}"',
        f'You have a new message from a buyer about "{ctx["propertyTitle"]}". Log in to HomeScape to respond.',
    ),
    "listingLive": lambda ctx: (
        f'Your listing "{ctx["title"]}" is live',
        f'"{ctx["title"]}" is now live on HomeScape and searchable by buyers.',
    ),
}


def send(template_name, to_email, context):
    if not to_email:
        return {"delivered": False, "reason": "no recipient email"}

    build = TEMPLATES.get(template_name)
    if not build:
        raise ValueError(f"Unknown notification template: {template_name}")
    subject, body = build(context)

    if not settings.EMAIL_BACKEND_CONFIGURED:
        logger.info("(console fallback) -> %s | Subject: %s | %s", to_email, subject, body)
        return {"delivered": False, "reason": "SMTP not configured, logged only"}

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    return {"delivered": True}
