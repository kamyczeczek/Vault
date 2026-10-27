import urllib.request
import json

queries = [
    "https://r.jina.ai/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=financial+forecasting+targets+directional+classification",
    "https://r.jina.ai/https://arxiv.org/abs/financial+time+series+forecasting+goals"
]

for url in queries[:1]:
    print(f"Querying via agent-reach web search (Jina Reader): {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "agent-reach/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(content[:1500])
    except Exception as e:
        print(f"Error: {e}")
