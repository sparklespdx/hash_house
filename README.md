# Hash House

This service stores messages for us. It hashes all incoming messages using SHA256 and return the hex digest upon storage. It will retrieve messages given a valid SHA256 hex digest that matches a previously stored message.


### Set Up Development Environment

The following commands will download the source code and run the development server on 127.0.0.1:5000.

Please provide AWS credentials to the shell before continuing, using either environment variables or a credentials file. You will also need the path of an S3 bucket to use for the project. Please see the `terraform/` directory for an example of how to set those up.

```
export S3_BUCKET_NAME=example-bucket-name
git clone https://github.com/sparklespdx/hash_house
cd hash_house
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 run_dev.py
```


### Endpoints

* / shows a help message
* /submit accepts POST requests to upload a new message in JSON format. The request body should look like this: `{"message": "foobar"}`. The Content-Type should be "application/json".
* /messages/$HEXDIGEST accepts GET requests to retrieve a message given a hex digest. An example would look like this: `curl https://hashhouse.moop.energy/messages/798f012674b5b8dcab4b00114bdf6738a69a4cdcf7ca0db1149260c9f81b73f7`


### Authentication

All requests to this service must have a Bearer token in the Authorization header. This would look like this:

```
curl -H "Authorization: Bearer example-api-key" https://hashhouse.moop.energy
```

Your API key must match a bcrypt hash stored in a JSON file on the server. We're using hashes here so we don't have to store our API keys in plaintext on the server.

The path for this file is set using the `APIKEY_FILE_PATH` environment variable (see `hash_house/config.py`). The default path is `/root/hashhouse_keys.json`. The format of the file should look like this:

```
{"$AAAb$AAA$AAAAAAAAAA.YXuIX3ykfsuzeXAAAAAAAAAAAAAAAAAAA": "josh"}
```

The keys are bcrypt hashes, stored as strings, and the values are usernames. You can have multiple users, just put multiple keys and values in the JSON object.

To generate a bcrypt hash from an API key, use the following example command replacing the placeholder key with a securely generated API key (make sure to install bcrypt using pip first):

```
python3 -c "import bcrypt; bcrypt.hashpw(b"my-new-api-key", bcrypt.gensalt())"
```

I recommend using `pwgen` to generate passwords and keys.


### Deployment

This service is currently deployed to a bare metal system using the Systemd unit file and nginx configuration found in `deploy/` and the Dockerfile found in the root of the project. The Systemd unit is "self-deploying", it just needs AWS credentials and an API key JSON file to be provided to it. See `hash_house.service` for more information.

Hash House could also be deployed using container orchestration such as Kubernetes or an app engine like Heroku.
