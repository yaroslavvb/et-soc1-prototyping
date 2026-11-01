#!/usr/bin/env python3
"""Search NASA's public image library (images-api.nasa.gov) and print candidates for the image inputs."""
import json, sys, urllib.parse, urllib.request
QS = ["bald eagle Kennedy Space Center", "alligator Kennedy Space Center", "pelican Kennedy Space Center",
      "manatee Kennedy Space Center", "space shuttle launch", "airplane on runway", "sea turtle", "owl", "deer Kennedy",
      "tractor", "school bus", "pickup truck", "fire truck", "bicycle", "dog", "cat", "volcano", "beach", "lighthouse", "sailboat"]
out = []
for q in QS:
    u = "https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image", "page_size": 15})
    d = json.load(urllib.request.urlopen(u, timeout=60))
    n = 0
    for it in d["collection"]["items"]:
        m = it["data"][0]
        txt = (m.get("description") or "") + " " + (m.get("title") or "") + " " + str(m.get("secondary_creator", "")) + " " + str(m.get("photographer", ""))
        if any(w in txt.lower() for w in ("copyright", "©", "getty", "courtesy", "reuters", "ap photo")):
            continue
        out.append({"q": q, "id": m["nasa_id"], "title": m.get("title"), "center": m.get("center"), "date": m.get("date_created"),
                    "photographer": m.get("photographer"), "desc": (m.get("description") or "")[:140]})
        n += 1
        if n >= 6:
            break
json.dump(out, sys.stdout, indent=0)
