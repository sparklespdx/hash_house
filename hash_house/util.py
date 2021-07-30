from functools import wraps
from flask import request, abort

import json
import logging
import os
import random
import uuid

from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


def limit_content_length(max_length):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cl = request.content_length
            if cl is not None and cl > max_length:
                abort(413)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Borrowed from https://docs.aws.amazon.com/code-samples/latest/catalog/python-s3-s3_basics-object_wrapper.py.html
def put_object(bucket, object_key, data):
    """
    Upload data to a bucket and identify it with the specified object key.

    Usage is shown in usage_demo at the end of this module.

    :param bucket: The bucket to receive the data.
    :param object_key: The key of the object in the bucket.
    :param data: The data to upload. This can either be bytes or a string. When this
                 argument is a string, it is interpreted as a file name, which is
                 opened in read bytes mode.
    """
    put_data = data
#    if isinstance(data, str):
#        try:
#            put_data = open(data, 'rb')
#        except IOError:
#            logger.exception("Expected file name or binary data, got '%s'.", data)
#            raise

    try:
        obj = bucket.Object(object_key)
        obj.put(Body=put_data)
        obj.wait_until_exists()
        logger.info("Put object '%s' to bucket '%s'.", object_key, bucket.name)
    except ClientError:
        logger.exception("Couldn't put object '%s' to bucket '%s'.",
                         object_key, bucket.name)
        raise
    finally:
        if getattr(put_data, 'close', None):
            put_data.close()


def get_object(bucket, object_key):
    """
    Gets an object from a bucket.

    Usage is shown in usage_demo at the end of this module.

    :param bucket: The bucket that contains the object.
    :param object_key: The key of the object to retrieve.
    :return: The object data in bytes.
    """
    try:
        body = bucket.Object(object_key).get()['Body'].read()
        logger.info("Got object '%s' from bucket '%s'.", object_key, bucket.name)
    except ClientError:
        logger.exception(("Couldn't get object '%s' from bucket '%s'.",
                          object_key, bucket.name))
        raise
    else:
        return body
