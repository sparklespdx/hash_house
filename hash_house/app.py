from flask import Flask, request
import json
import hashlib
import re

from hash_house.util import limit_content_length

class Storage:

    def get(self, key):
        return 'foobar'

    def save(self, key, value):
        return True


class Message:

    def __init__(self):
        self._hash = None
        self.body = None
        self.storage = Storage()

    def _do_hashing(self, content):
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get(self, _hash):
        self.body = self.storage.get(_hash)
        self._hash = _hash

    def save(self, body):
        self.body = body
        self._hash = self._do_hashing(self.body)
        self.storage.save(self._hash, self.body)


app = Flask(__name__)
app.config.from_object("hash_house.config.Config")


@app.route("/")
def root():
    return json.dumps({"info": "Welcome to Hash House. POST to /submit to store a string message and get a hash (something like this: {'message': 'foo'}). GET /messages/$HEXDIGEST to retrieve a message."}), 200


@app.route("/submit", methods=["POST"])
@limit_content_length(app.config['MAX_CONTENT_LENGTH'])
def submit_message():
    payload = request.get_json()

    if "message" not in payload:
        return json.dumps({"error": "'message' key not present in payload"}), 400

    if len(payload['message']) > app.config['UPLOAD_SIZE_LIMIT']:
        return json.dumps({"error": f"'message' is longer than {str(app.config['UPLOAD_SIZE_LIMIT'] / 1024 / 1024)}M"}), 400

    message = Message()
    message.save(payload['message'])
    return json.dumps({"hash": str(message._hash)}), 200


@app.route("/messages/<_hash>", methods=["GET"])
def retrieve_message(_hash):

    error = json.dumps({"error": "/messages/$HASH must be a sha256 hex digest."})

    # Basic check so we use less regex
    if len(_hash) != 64:
        return error, 400

    # Regex match for sha256 hex digest as a string
    if re.match('^[a-fA-F0-9]{64}$', _hash) is None:
        return error, 400

    message = Message()
    message.get(_hash)
    if message.body is not None:
        return json.dumps({"message": message.body}), 200

    return json.dumps({"error": "not found"}), 404

