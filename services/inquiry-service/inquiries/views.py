import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import Inquiry, InquiryResponse
from .permissions import IsAuthenticatedStateless
from .serializers import InquirySerializer


class CreateInquiryView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request):
        property_id = request.data.get("propertyId")
        message = request.data.get("message")
        inquiry_type = request.data.get("type", "message")
        offer_amount = request.data.get("offerAmount")
        requested_time = request.data.get("requestedTime")

        if not property_id or not message:
            return Response({"error": "propertyId and message are required"}, status=400)

        try:
            prop_res = requests.get(f"{settings.INTERNAL_SERVICE_URLS['property']}/{property_id}", timeout=5)
        except requests.RequestException:
            return Response({"error": "Property not found"}, status=404)
        if prop_res.status_code != 200:
            return Response({"error": "Property not found"}, status=404)
        prop = prop_res.json()

        inquiry = Inquiry.objects.create(
            property_id=property_id,
            buyer_id=request.user.id,
            seller_id=prop["seller_id"],
            type=inquiry_type,
            message=message,
            offer_amount=offer_amount,
            requested_time=requested_time,
        )

        publish_event(
            "InquiryCreated",
            {
                **InquirySerializer(inquiry).data,
                "propertyTitle": prop["title"],
                "buyerId": str(request.user.id),
            },
        )
        return Response(InquirySerializer(inquiry).data, status=201)


class MyInquiriesView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Inquiry.objects.filter(buyer_id=request.user.id).order_by("-created_at")
        return Response(InquirySerializer(qs, many=True).data)


class ReceivedInquiriesView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Inquiry.objects.filter(seller_id=request.user.id).order_by("-created_at")
        return Response(InquirySerializer(qs, many=True).data)


class RespondToInquiryView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request, pk):
        message = request.data.get("message")
        status_value = request.data.get("status")
        if not message:
            return Response({"error": "message is required"}, status=400)

        try:
            inquiry = Inquiry.objects.get(id=pk)
        except (Inquiry.DoesNotExist, ValueError):
            return Response({"error": "Inquiry not found"}, status=404)
        if str(inquiry.seller_id) != str(request.user.id):
            return Response({"error": "Only the recipient seller can respond"}, status=403)

        InquiryResponse.objects.create(inquiry=inquiry, author_id=request.user.id, message=message)

        valid_statuses = ["responded", "scheduled", "accepted", "declined", "closed"]
        inquiry.status = status_value if status_value in valid_statuses else "responded"
        inquiry.save(update_fields=["status", "updated_at"])

        publish_event("InquiryResponded", InquirySerializer(inquiry).data)
        return Response(InquirySerializer(inquiry).data)
