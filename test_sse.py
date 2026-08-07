import urllib.request
import json

url = "http://localhost:8000/api/research?topic=What+is+5+times+12"
req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
try:
    with urllib.request.urlopen(req, timeout=30) as response:
        print("SSE connected, status:", response.getcode())
        events = 0
        for line in response:
            line = line.decode("utf-8").strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                etype = data.get("type", "")
                detail = data.get("display", data.get("message", ""))
                if etype == "final_report":
                    detail = data.get("report", "")[:80]
                print("  Event %d: %s - %s" % (events + 1, etype, detail))
                events += 1
                if etype == "final_report":
                    break
        print("Total events: %d" % events)
        print("SSE TEST: PASS")
except Exception as e:
    print("SSE TEST FAIL: %s" % e)
