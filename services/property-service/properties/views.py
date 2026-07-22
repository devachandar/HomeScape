from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import Favorite, Property, PropertyAmenity, PropertyImage
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import PropertyListSerializer, PropertySerializer


def _camel(snake_field: str) -> str:
    parts = snake_field.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class PropertyListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsRole("seller", "agent", "admin")]
        return []

    def get(self, request):
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
        except ValueError:
            page = 1
        try:
            limit = min(int(request.query_params.get("limit", 20)), 100)
        except ValueError:
            limit = 20
        offset = (page - 1) * limit

        qs = Property.objects.filter(status="active").order_by("-created_at")[offset : offset + limit]
        return Response({"page": page, "limit": limit, "results": PropertyListSerializer(qs, many=True).data})

    def post(self, request):
        data = request.data
        title = data.get("title")
        price = data.get("price")
        address_line1 = data.get("addressLine1") or data.get("address_line1")
        city = data.get("city")
        state = data.get("state")
        postal_code = data.get("postalCode") or data.get("postal_code")
        if not all([title, price, address_line1, city, state, postal_code]):
            return Response(
                {"error": "title, price, addressLine1, city, state and postalCode are required"}, status=400
            )

        prop = Property.objects.create(
            seller_id=request.user.id,
            title=title,
            description=data.get("description") or "",
            property_type=data.get("propertyType") or data.get("property_type") or "house",
            status="active",
            price=price,
            bedrooms=data.get("bedrooms") or 0,
            bathrooms=data.get("bathrooms") or 0,
            square_feet=data.get("squareFeet") or data.get("square_feet"),
            address_line1=address_line1,
            address_line2=data.get("addressLine2") or data.get("address_line2") or "",
            city=city,
            state=state,
            postal_code=postal_code,
            country=data.get("country") or "USA",
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            available_from=data.get("availableFrom") or data.get("available_from"),
        )

        for i, url in enumerate(data.get("images") or []):
            PropertyImage.objects.create(property=prop, url=url, sort_order=i)
        for amenity in data.get("amenities") or []:
            PropertyAmenity.objects.get_or_create(property=prop, amenity=amenity)

        full = PropertySerializer(prop).data
        publish_event("PropertyCreated", full)
        return Response(full, status=201)


class SellerMinePropertiesView(APIView):
    permission_classes = [IsRole("seller", "agent", "admin")]

    def get(self, request):
        qs = Property.objects.filter(seller_id=request.user.id).order_by("-created_at")
        return Response(PropertyListSerializer(qs, many=True).data)


class MyFavoritesView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        favorite_ids = list(Favorite.objects.filter(user_id=request.user.id).values_list("property_id", flat=True))
        qs = Property.objects.filter(id__in=favorite_ids).order_by("-created_at")
        return Response(PropertyListSerializer(qs, many=True).data)


class PropertyDetailView(APIView):
    """GET is public; PATCH/DELETE require the owning seller (or admin) -
    same mixed-auth shape as the original single Express route, just split
    across DRF methods on one class. `UNAUTHENTICATED_USER = None` in
    settings is what makes `request.user` reliably `None` (not
    AnonymousUser) here when no token is present."""

    permission_classes = []

    def get(self, request, pk):
        try:
            prop = Property.objects.get(id=pk)
        except (Property.DoesNotExist, ValueError):
            return Response({"error": "Property not found"}, status=404)
        publish_event("PropertyViewed", {"propertyId": str(pk)})
        return Response(PropertySerializer(prop).data)

    def patch(self, request, pk):
        if not request.user or request.user.role not in ("seller", "agent", "admin"):
            return Response({"error": "Insufficient permissions"}, status=403)
        try:
            prop = Property.objects.get(id=pk)
        except (Property.DoesNotExist, ValueError):
            return Response({"error": "Property not found"}, status=404)
        if str(prop.seller_id) != str(request.user.id) and request.user.role != "admin":
            return Response({"error": "You do not own this listing"}, status=403)

        fields = [
            "title", "description", "property_type", "status", "price", "bedrooms", "bathrooms",
            "square_feet", "address_line1", "address_line2", "city", "state", "postal_code",
            "country", "latitude", "longitude", "available_from",
        ]
        camel_map = {_camel(f): f for f in fields}
        updated = False
        for key, value in request.data.items():
            column = camel_map.get(key, key if key in fields else None)
            if column:
                setattr(prop, column, value)
                updated = True
        if not updated:
            return Response({"error": "No valid fields to update"}, status=400)
        prop.save()

        full = PropertySerializer(prop).data
        publish_event("PropertyUpdated", full)
        return Response(full)

    def delete(self, request, pk):
        if not request.user or request.user.role not in ("seller", "agent", "admin"):
            return Response({"error": "Insufficient permissions"}, status=403)
        try:
            prop = Property.objects.get(id=pk)
        except (Property.DoesNotExist, ValueError):
            return Response({"error": "Property not found"}, status=404)
        if str(prop.seller_id) != str(request.user.id) and request.user.role != "admin":
            return Response({"error": "You do not own this listing"}, status=403)
        prop.delete()
        publish_event("PropertyDeleted", {"propertyId": str(pk)})
        return Response(status=204)


class FavoriteView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request, pk):
        Favorite.objects.get_or_create(user_id=request.user.id, property_id=pk)
        return Response(status=204)

    def delete(self, request, pk):
        Favorite.objects.filter(user_id=request.user.id, property_id=pk).delete()
        return Response(status=204)
