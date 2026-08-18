import os

BASE_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "app",
    "static",
    "uploads",
    "products"
)

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}