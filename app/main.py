# Based on the Python example for "Authentication" from Kraken documentation: https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature

import urllib.parse
import hashlib
import hmac
import base64
import requests
import time

# Base API URL used in all Kraken requests
api_url = "https://api.kraken.com"

# Get secret keys from local `.env` file
with open(".env", "r") as file:
  lines = file.read().splitlines()
  api_key = lines[0] # Public API key 
  api_secret = lines[1] # Private API key

# Used as "nonce" for Kraken requests
# "Nonce must be an always increasing, unsigned 64-bit integer, for each request that is made with a particular API key."
# https://docs.kraken.com/rest/#section/Authentication/Nonce-and-2FA
def get_utc_time_in_milliseconds():
  return str(int(1000 * time.time()))

# "Authenticated requests should be signed with the "API-Sign" header, using a signature generated with your private key, nonce, encoded payload, and URI path according to:
# HMAC-SHA512 of (URI path + SHA256(nonce + POST data)) and base64 decoded secret API key"
# https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature
def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

# Request factory using the `requests` library
def make_kraken_request(url_path, data):
  headers = {
    "API-Key": api_key,
    "API-Sign": get_kraken_signature(url_path, data, api_secret)
  }
  return requests.post((api_url + url_path), headers=headers, data=data)

resp = make_kraken_request(
  "/0/private/Balance",
  { "nonce": get_utc_time_in_milliseconds() }
)

print(resp.json())