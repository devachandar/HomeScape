from rest_framework import serializers

from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = [
            "id", "property_id", "buyer_id", "seller_id", "type", "status",
            "message", "offer_amount", "requested_time", "created_at", "updated_at",
        ]
