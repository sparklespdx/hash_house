import os


class Config:

    # Default 10MB/11MB
    UPLOAD_SIZE_LIMIT = int(os.environ.get("UPLOAD_SIZE_LIMIT", 1024 * 1024 * 10))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 1024 * 1024 * 11))

    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", '')

    APIKEY_FILE_PATH = os.environ.get("APIKEY_FILE_PATH", "/root/hashhouse_keys.json")
    APIKEY_MAX_LENGTH = int(os.environ.get("APIKEY_MAX_LENGTH", 128))
