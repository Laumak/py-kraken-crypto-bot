# Based on the Python example for "Authentication" from Kraken documentation: https://docs.kraken.com/rest/#section/Authentication/Headers-and-Signature

import urllib.parse
import hashlib
import hmac
import base64
import requests
import time

# Base API URL used in all Kraken requests
api_url = "https://api.kraken.com"

buy_limit = 100
buy_amount = 0.01
sell_limit = 50000
sell_amount = 0.01

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
def make_kraken_request(url_path, data={}):
  data_with_nonce = {
    "nonce": get_utc_time_in_milliseconds(),
    **data
  }
  headers = {
    "API-Key": api_key,
    "API-Sign": get_kraken_signature(url_path, data_with_nonce, api_secret)
  }
  return requests.post((api_url + url_path), headers=headers, data=data_with_nonce)

# Balance
def get_balance():
  return make_kraken_request(
    "/0/private/Balance"
  ).json()

print("Balance:", get_balance()["result"])

# Sell order
def make_market_sell_order():
  return make_kraken_request(
    "/0/private/AddOrder",
    {
      "ordertype": "market",
      "type": "sell",
      "volume": sell_amount,
      "pair": "XBTUSD",
    }
  ).json()

# Purcase order
def make_market_purchase_order():
  return make_kraken_request(
    "/0/private/AddOrder",
    {
      "ordertype": "market",
      "type": "buy",
      "volume": 0.01,
      "pair": "XBTUSD",
      "price": 100
    }
  ).json()

"""
Check current price for "XXBTZUSD" and either sell of buy said coin based on the current value
"""
while True:
  """
  Example response:
  {
    'error': [],
    'result': {
      'XXBTZUSD': {
        'a': ['23729.30000', '1', '1.000'],
        'b': ['23725.20000', '1', '1.000'],
        'c': ['23707.90000', '0.00132957'],
        'v': ['560.00209407', '2504.84056307'],
        'p': ['23761.90917', '24103.56103'],
        't': [8489, 22248],
        'l': ['23550.10000', '23525.60000'],
        'h': ['23886.30000', '24614.90000'],
        'o': '23646.50000'
      }
    }
  }
  """
  current_price_json = requests.get(api_url + "/0/public/Ticker?pair=BTCUSD").json()
  current_price = current_price_json['result']['XXBTZUSD']['c'][0]

  print(current_price)

  if float(current_price) < buy_limit:
    print(f"Buying {buy_amount} of BTC at {current_price}!")

    resp = make_market_purchase_order()
    error = resp["error"]

    if not error:
      print("Successfully bought BTC")
    else:
      print(f"Error: {error}")
  
  elif float(current_price) > sell_limit:
    resp = make_market_sell_order()
    error = resp["error"]

    if not error:
      print("Successfully sold BTC")
    else:
      print(f"Error: {error}")

  else:
    print(f"Current price is: {current_price}. Not buying or selling...")
    print(f"Highest limit for buying is {buy_limit}")
    print(f"Lowest limit for selling is {sell_limit}")

  time.sleep(3)