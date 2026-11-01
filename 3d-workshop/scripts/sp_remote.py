# Usage: python sp_remote.py <script.py>   (Painter must be started with --enable-remote-scripting)
# Sends a Python snippet to Painter's remote scripting server and prints the result.
import base64
import json
import sys
import urllib.request

code = open(sys.argv[1], encoding="utf-8").read()
body = json.dumps({"python": base64.b64encode(code.encode()).decode()}).encode()
req = urllib.request.Request("http://[::1]:60041/run.json", data=body, headers={"Content-Type": "application/json"})
print(urllib.request.urlopen(req, timeout=600).read().decode())
