import os


class Config:

    # Default 10MB
    UPLOAD_SIZE_LIMIT = os.environ.get("UPLOAD_SIZE_LIMIT", 1024 * 1024 * 10)
