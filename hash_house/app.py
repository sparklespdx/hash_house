import bcrypt
import boto3
import hashlib
import json
import re

from flask import Flask, request
from flask_httpauth import HTTPTokenAuth

from botocore.exceptions import ClientError

from hash_house.util import limit_content_length, put_object, get_object


class Storage:

    def __init__(self, s3_bucket):
        self.bucket = s3_bucket

    def get(self, key):
        try:
            item = get_object(self.bucket, key) 
        except ClientError:
            item = None
        return item

    def save(self, key, value):
        put_object(self.bucket, key, value)


class Message:

    def __init__(self, storage):
        self._hash = None
        self.body = None
        self.storage = storage

    def _do_hashing(self, content):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, _hash):
        self.body = self.storage.get(_hash).decode("utf-8")
        self._hash = _hash

    def save(self, body):
        self.body = body
        self._hash = self._do_hashing(self.body)
        self.storage.save(self._hash, self.body)


app = Flask(__name__)
app.config.from_object("hash_house.config.Config")


s3 = boto3.resource('s3')
bucket = s3.Bucket(app.config['S3_BUCKET_NAME'])
storage = Storage(bucket)


auth = HTTPTokenAuth(scheme='Bearer')
with open(app.config['APIKEY_FILE_PATH'], 'r') as f:
    tokens = json.loads(f.read())


@auth.verify_token
def verify_token(token):
    for t in tokens:
        if bcrypt.checkpw(token.encode('utf-8'), t.encode('utf-8')):
            return tokens[t]


@app.route("/")
@auth.login_required
def root():
    return json.dumps({"info": "Welcome to Hash House. POST to /submit to store a string message and get a hash (something like this: {'message': 'foo'}). GET /messages/$HEXDIGEST to retrieve a message."}), 200


@app.route("/submit", methods=['POST'])
@auth.login_required
@limit_content_length(app.config['MAX_CONTENT_LENGTH'])
def submit_message():

    payload = request.get_json()

    if "message" not in payload:
        return json.dumps({"error": "'message' key not present in payload"}), 400

    if len(payload['message']) > app.config['UPLOAD_SIZE_LIMIT']:
        return json.dumps({"error": f"'message' is longer than {str(app.config['UPLOAD_SIZE_LIMIT'] / 1024 / 1024)}M"}), 400

    message = Message(storage)
    #try:
    message.save(payload['message'])
    return json.dumps({"hash": str(message._hash)}), 200
    #except:
    #    return json.dumps({"error": "message not stored successfully"}), 500


@app.route("/messages/<_hash>", methods=['GET'])
@auth.login_required
def retrieve_message(_hash):

    error = json.dumps({"error": "/messages/$HASH must be a sha256 hex digest."})

    # Basic check so we use less regex
    if len(_hash) != 64:
        return error, 400

    # Regex match for sha256 hex digest as a string
    if re.match("^[a-fA-F0-9]{64}$", _hash) is None:
        return error, 400

    message = Message(storage)
    message.get(_hash)
    if message.body is not None:
        return json.dumps({"message": message.body}), 200

    return json.dumps({"error": "not found"}), 404

