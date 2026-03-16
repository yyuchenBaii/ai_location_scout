import urllib.request
import json
import urllib.parse
import os
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

import sys

key = os.environ.get("AMAP_WEB_KEY")
address_str = sys.argv[1] if len(sys.argv) > 1 else "上海市静安寺"
address = urllib.parse.quote(address_str)
url = f"https://restapi.amap.com/v3/geocode/geo?address={address}&key={key}"

req = urllib.request.Request(url)
with urllib.request.urlopen(req, context=ctx) as response:
    res = json.loads(response.read())
    if res['status'] == '1' and res['geocodes']:
        print(res['geocodes'][0]['location'])
    else:
        print("Failed to geocode")
