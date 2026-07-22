from rest_framework.response import Response
from rest_framework.views import APIView

from .es import INDEX, ensure_index, get_client


class SearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_index()
        params = request.query_params
        q = params.get("q")
        city = params.get("city")
        property_type = params.get("propertyType")
        min_price = params.get("minPrice")
        max_price = params.get("maxPrice")
        bedrooms = params.get("bedrooms")
        bathrooms = params.get("bathrooms")
        amenities = params.get("amenities")
        lat, lon, radius_km = params.get("lat"), params.get("lon"), params.get("radiusKm")
        sort = params.get("sort", "relevance")
        page = int(params.get("page", 1))
        limit = min(int(params.get("limit", 20)), 100)

        must = [{"term": {"status": "active"}}]
        filter_clauses = []

        if q:
            must.append(
                {"multi_match": {"query": q, "fields": ["title^3", "description", "city^2", "state"], "fuzziness": "AUTO"}}
            )
        if city:
            filter_clauses.append({"term": {"city": city.lower()}})
        if property_type:
            filter_clauses.append({"term": {"property_type": property_type}})
        if bedrooms:
            filter_clauses.append({"range": {"bedrooms": {"gte": int(bedrooms)}}})
        if bathrooms:
            filter_clauses.append({"range": {"bathrooms": {"gte": float(bathrooms)}}})
        if min_price or max_price:
            price_range = {}
            if min_price:
                price_range["gte"] = float(min_price)
            if max_price:
                price_range["lte"] = float(max_price)
            filter_clauses.append({"range": {"price": price_range}})
        if amenities:
            for amenity in amenities.split(","):
                filter_clauses.append({"term": {"amenities": amenity}})
        if lat and lon and radius_km:
            filter_clauses.append(
                {"geo_distance": {"distance": f"{radius_km}km", "location": {"lat": float(lat), "lon": float(lon)}}}
            )

        sort_clause = (
            [{"price": "asc"}]
            if sort == "price_asc"
            else [{"price": "desc"}]
            if sort == "price_desc"
            else [{"created_at": "desc"}]
            if sort == "newest"
            else ["_score"]
        )

        result = get_client().search(
            index=INDEX,
            from_=(page - 1) * limit,
            size=limit,
            query={"bool": {"must": must, "filter": filter_clauses}},
            sort=sort_clause,
        )

        return Response(
            {
                "total": result["hits"]["total"]["value"],
                "page": page,
                "limit": limit,
                "results": [{"id": hit["_id"], "score": hit["_score"], **hit["_source"]} for hit in result["hits"]["hits"]],
            }
        )


class AutocompleteView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_index()
        q = request.query_params.get("q")
        if not q:
            return Response({"suggestions": []})

        result = get_client().search(
            index=INDEX,
            size=8,
            query={
                "multi_match": {
                    "query": q,
                    "type": "bool_prefix",
                    "fields": ["title.autocomplete", "title.autocomplete._2gram", "title.autocomplete._3gram"],
                }
            },
            source=["title", "city", "state"],
        )
        return Response({"suggestions": [{"id": hit["_id"], **hit["_source"]} for hit in result["hits"]["hits"]]})
