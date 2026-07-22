from rest_framework import serializers

from .models import Favorite, Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "url", "sort_order"]


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id", "seller_id", "title", "description", "property_type", "status", "price",
            "bedrooms", "bathrooms", "square_feet", "address_line1", "address_line2", "city",
            "state", "postal_code", "country", "latitude", "longitude", "available_from",
            "images", "amenities", "created_at", "updated_at",
        ]

    def get_amenities(self, obj):
        return [row.amenity for row in obj.amenity_rows.all()]


class PropertyListSerializer(serializers.ModelSerializer):
    """Used for plain list endpoints (GET /, GET /seller/mine) where the
    original Node service returned bare rows without the nested
    images/amenities - kept identical here to avoid an N+1 on listings."""

    class Meta:
        model = Property
        fields = [
            "id", "seller_id", "title", "description", "property_type", "status", "price",
            "bedrooms", "bathrooms", "square_feet", "address_line1", "address_line2", "city",
            "state", "postal_code", "country", "latitude", "longitude", "available_from",
            "created_at", "updated_at",
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ["user_id", "created_at"]
