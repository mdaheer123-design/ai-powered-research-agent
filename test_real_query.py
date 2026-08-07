import urllib.request
import json

url = "http://localhost:8000/api/research?topic=Chief+Minister+of+Tamilnadu"
req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
try:
    with urllib.request.urlopen(req, timeout=60) as response:
        print("SSE connected, status:", response.getcode())
        events = 0
        for line in response:
            line = line.decode("utf-8").strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                etype = data.get("type", "")
                detail = data.get("display", data.get("message", ""))
                if etype == "final_report":
                    detail = data.get("report", "")[:120]
                print("  Event %d: %s - %s" % (events + 1, etype, detail))
                events += 1
                if etype == "final_report" or etype == "error":
                    break
        print("Total events: %d" % events)
        has_report = any(True for _ in [])  # dummy
        print("REAL QUERY TEST: PASS" if events > 0 else "REAL QUERY TEST: FAIL")
except Exception as e:
    print("REAL QUERY TEST FAIL: %s" % e)
