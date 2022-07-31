# Example from Kraken documentation: https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature

import urllib.parse
import hashlib
import hmac
import base64

api_url = "https://api.kraken.com"

with open(".env", "r") as f:
  lines = f.read().splitlines()
  api_key = lines[0]
  api_secret = lines[1]

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(url_path, data, api_key, api_secret):
  headers = {
    "API-Key": api_key,
    "API-Sign": get_kraken_signature(url_path, data, api_secret)
}
  return requests.post((api_url + url_path), headers=headers, data=data)


signature = get_kraken_signature("/0/private/AddOrder", data, api_secret)
print("API-Sign: {}".format(signature))