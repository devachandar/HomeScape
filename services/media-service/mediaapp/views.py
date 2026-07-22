from django.http import FileResponse, Http404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .storage import UPLOAD_DIR, save_file

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 8 * 1024 * 1024
MAX_FILES = 10


class UploadView(APIView):
    # Matches the original Node service - open upload endpoint, no auth
    # required. Kept identical rather than quietly tightening it, since
    # this is a language/framework swap, not a security pass.
    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist("images")
        if not files:
            return Response({"error": "No valid image files were provided"}, status=400)
        if len(files) > MAX_FILES:
            return Response({"error": f"You can upload at most {MAX_FILES} files at once"}, status=400)

        urls = []
        for f in files:
            if f.content_type not in ALLOWED_TYPES:
                continue
            if f.size > MAX_SIZE:
                continue
            urls.append(save_file(f))

        if not urls:
            return Response({"error": "No valid image files were provided"}, status=400)

        return Response({"urls": urls}, status=201)


class ServeUploadView(APIView):
    """Only relevant with STORAGE_DRIVER=local."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, filename):
        import os

        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            raise Http404
        return FileResponse(open(path, "rb"))
