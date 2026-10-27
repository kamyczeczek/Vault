import urllib.request
import json

url = "https://r.jina.ai/https://huggingface.co/blog/state-space-models"
req = urllib.request.Request(url, headers={"User-Agent": "agent-reach/1.0"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        text = resp.read().decode("utf-8")
        print(text[:2000])
except Exception as e:
    print("Error:", e)
