import uuid

from django.db import models


class Inquiry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_id = models.UUIDField()
    buyer_id = models.UUIDField()
    seller_id = models.UUIDField()
    type = models.CharField(
        max_length=20,
        choices=[("message", "Message"), ("viewing_request", "Viewing request"), ("offer", "Offer")],
        default="message",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("open", "Open"), ("responded", "Responded"), ("scheduled", "Scheduled"),
            ("accepted", "Accepted"), ("declined", "Declined"), ("closed", "Closed"),
        ],
        default="open",
    )
    message = models.TextField()
    offer_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    requested_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["buyer_id"]),
            models.Index(fields=["seller_id"]),
            models.Index(fields=["property_id"]),
        ]


class InquiryResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name="responses")
    author_id = models.UUIDField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
