import os
import uuid

from django.conf import settings

UPLOAD_DIR = os.path.join(settings.BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ext(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext or ".jpg"


def save_local(uploaded_file) -> str:
    filename = f"{uuid.uuid4().hex}{_ext(uploaded_file.name)}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    # Gateway-prefixed so the browser's request routes back through Nginx
    # to this same service, regardless of which page/origin renders the URL.
    return f"/api/media/uploads/{filename}"


def save_s3(uploaded_file) -> str:
    import boto3

    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    key = f"properties/{uuid.uuid4().hex}{_ext(uploaded_file.name)}"
    bucket = os.environ.get("S3_BUCKET")

    s3.upload_fileobj(uploaded_file, bucket, key, ExtraArgs={"ContentType": uploaded_file.content_type})

    cdn_base = os.environ.get("CDN_BASE_URL")
    region = os.environ.get("AWS_REGION", "us-east-1")
    return f"{cdn_base}/{key}" if cdn_base else f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def save_file(uploaded_file) -> str:
    driver = os.environ.get("STORAGE_DRIVER", "local")
    return save_s3(uploaded_file) if driver == "s3" else save_local(uploaded_file)
