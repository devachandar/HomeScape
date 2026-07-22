import uuid

from django.db import models


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller_id = models.UUIDField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    property_type = models.CharField(
        max_length=20,
        choices=[("house", "House"), ("apartment", "Apartment"), ("condo", "Condo"), ("townhouse", "Townhouse"), ("land", "Land")],
        default="house",
    )
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("pending_review", "Pending review"), ("active", "Active"), ("sold", "Sold"), ("removed", "Removed")],
        default="draft",
    )
    price = models.DecimalField(max_digits=14, decimal_places=2)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    square_feet = models.IntegerField(null=True, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="USA")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["status"]),
            models.Index(fields=["seller_id"]),
        ]


class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(max_length=500)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class PropertyAmenity(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="amenity_rows")
    amenity = models.CharField(max_length=100)

    class Meta:
        unique_together = ("property", "amenity")


class Favorite(models.Model):
    user_id = models.UUIDField()
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_id", "property")
