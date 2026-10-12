#!/usr/bin/env python3
"""
build_feeds.py — Generates RFC 5545 .ics calendar feeds for Festival Calendar.
Outputs feeds to site/ directory for hosting via GitHub Pages / webcal://.
"""

import json
import re
import datetime
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
DATA_PATH = SITE_DIR / "data.json"
DATES_PATH = SITE_DIR / "dates.json"

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def pad(n):
    return f"{n:02d}"

def fold_line(line, limit=74):
    """Fold lines longer than 75 octets per RFC 5545 Section 3.1."""
    if len(line.encode("utf-8")) <= limit:
        return line
    res = []
    current = ""
    for ch in line:
        test = current + ch
        if len(test.encode("utf-8")) > limit:
            res.append(current)
            current = " " + ch
        else:
            current = test
    if current:
        res.append(current)
    return "\r\n".join(res)

def compute_month_range(r, year=2026):
    m = str(r.get("month") or "").lower()
    start_idx = -1
    for idx, name in enumerate(MONTH_NAMES):
        if name[:3].lower() in m:
            start_idx = idx
            break
    if start_idx < 0:
        return ("01-01", "12-31")

    end_idx = start_idx
    for idx in range(start_idx + 1, len(MONTH_NAMES)):
        if MONTH_NAMES[idx][:3].lower() in m:
            end_idx = idx

    # Calculate last day of end_idx
    if end_idx == 11:
        last_day = 31
    else:
        next_month = datetime.date(year, end_idx + 2, 1)
        last_day = (next_month - datetime.timedelta(days=1)).day

    return (f"{pad(start_idx + 1)}-01", f"{pad(end_idx + 1)}-{pad(last_day)}")

def escape_ics(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return text

def create_vevent(f, now_stamp, current_year=2026):
    slug = re.sub(r"[^a-z0-9]+", "-", f.get("name", "event").lower()).strip("-")
    
    start_md = f.get("s")
    end_md = f.get("e")
    if not start_md or not end_md:
        return None

    sm, sd = [int(x) for x in start_md.split("-")]
    em, ed = [int(x) for x in end_md.split("-")]

    start_date = datetime.date(current_year, sm, sd)
    # Handle events spanning across year boundary (e.g. Dec to Jan)
    end_year = current_year if start_md <= end_md else current_year + 1
    end_date = datetime.date(end_year, em, ed)
    # In RFC 5545, DTEND for all-day VALUE=DATE is non-inclusive (day after)
    exclusive_end = end_date + datetime.timedelta(days=1)

    dtstart_str = start_date.strftime("%Y%m%d")
    dtend_str = exclusive_end.strftime("%Y%m%d")
    uid = f"{slug}-{dtstart_str}@chid.github.io"

    # Description text
    desc_parts = []
    if f.get("city"):
        desc_parts.append(f"City: {f['city']}")
    if f.get("category"):
        desc_parts.append(f"Category: {f['category']}")
    if f.get("price_tier"):
        tier = f['price_tier']
        detail = f.get('price_detail')
        desc_parts.append(f"Pricing: {tier}" + (f" ({detail})" if detail else ""))
    if f.get("dates"):
        desc_parts.append(f"Dates Note: {f['dates']}")
    if f.get("notes"):
        desc_parts.append(f"Note: {f['notes']}")
    if f.get("url"):
        desc_parts.append(f"Website: {f['url']}")

    desc = escape_ics("\n\n".join(desc_parts))
    summary = escape_ics(f.get("name", "Festival"))
    location = escape_ics(f"{f.get('venue') or f.get('city')}, {f.get('city')}, Australia")

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now_stamp}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        f"LOCATION:{location}",
        f"DTSTART;VALUE=DATE:{dtstart_str}",
        f"DTEND;VALUE=DATE:{dtend_str}",
        "STATUS:CONFIRMED",
        "TRANSP:TRANSPARENT"
    ]
    if f.get("url"):
        lines.append(f"URL:{f['url']}")
    lines.append("END:VEVENT")

    return "\r\n".join(fold_line(line) for line in lines)

def build_feed(calendar_name, description, festivals, now_stamp):
    events = []
    for f in festivals:
        ev = create_vevent(f, now_stamp)
        if ev:
            events.append(ev)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//chid//Festival Register//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{escape_ics(calendar_name)}",
        f"X-WR-CALDESC:{escape_ics(description)}",
        "X-WR-TIMEZONE:Australia/Sydney",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D"
    ]
    
    header = "\r\n".join(fold_line(line) for line in lines)
    body = "\r\n".join(events)
    return f"{header}\r\n{body}\r\nEND:VCALENDAR\r\n"

def main():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    festivals = data.get("festivals", [])

    date_map = {}
    if DATES_PATH.exists():
        with open(DATES_PATH, "r", encoding="utf-8") as f:
            for item in json.load(f):
                date_map[f"{item.get('city')}|{item.get('name')}"] = item

    for r in festivals:
        key = f"{r.get('city')}|{r.get('name')}"
        dm = date_map.get(key)
        if dm and dm.get("basis") == "unknown":
            r["s"] = r["e"] = ""
            r["basis"] = "unknown"
        elif dm and dm.get("start"):
            r["s"] = dm["start"]
            r["e"] = dm["end"]
            r["basis"] = dm.get("basis", "edition-dates")
        else:
            s, e = compute_month_range(r)
            r["s"] = s
            r["e"] = e
            r["basis"] = "month-only"

    now_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    feeds = [
        {
            "filename": "festivals-all.ics",
            "name": "Festival Calendar (All Cities)",
            "desc": "Verified recurring festivals in Sydney, Melbourne, and Canberra",
            "festivals": festivals
        },
        {
            "filename": "festivals-sydney.ics",
            "name": "Festival Calendar — Sydney Circuit",
            "desc": "Verified festivals and major recurring events across Greater Sydney",
            "festivals": [f for f in festivals if f.get("city") == "Sydney"]
        },
        {
            "filename": "festivals-melbourne.ics",
            "name": "Festival Calendar — Melbourne Stages",
            "desc": "Verified festivals and major recurring events across Melbourne & Victoria",
            "festivals": [f for f in festivals if f.get("city") == "Melbourne"]
        },
        {
            "filename": "festivals-canberra.ics",
            "name": "Festival Calendar — Canberra Events",
            "desc": "Verified festivals and cultural showcases across the ACT",
            "festivals": [f for f in festivals if f.get("city") == "Canberra"]
        },
        {
            "filename": "festivals-free.ics",
            "name": "Festival Calendar — Free Entry",
            "desc": "Verified free festivals with $0 admission across Sydney, Melbourne & Canberra",
            "festivals": [f for f in festivals if f.get("price_tier") == "Free"]
        }
    ]

    for feed in feeds:
        out_path = SITE_DIR / feed["filename"]
        content = build_feed(feed["name"], feed["desc"], feed["festivals"], now_stamp)
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(content)
        print(f"Generated {feed['filename']}: {len(feed['festivals'])} festivals -> {out_path.stat().st_size} bytes")

if __name__ == "__main__":
    main()
