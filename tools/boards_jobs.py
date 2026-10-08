#!/usr/bin/env python3
"""Job boards beyond LinkedIn and company careers pages. Stdlib only, public APIs and feeds only.

  python tools/boards_jobs.py hn            # latest HN "Who is hiring?" thread (monthly)
  python tools/boards_jobs.py himalayas     # Himalayas remote board (location restrictions + salary)
  python tools/boards_jobs.py getro         # VC portfolio boards from knowledge.json → vc_boards
  python tools/boards_jobs.py wwr           # We Work Remotely RSS feeds
  python tools/boards_jobs.py all

Every source goes through the same title and location rules as tools/ats_jobs.py, taken from
profile/knowledge.json → filters. Search phrases for Himalayas and Getro come from
knowledge.json → search.board_queries (default: your first four target titles). Remote roles tied to
places outside your remote rule are dropped unless --include-restricted. Output is JSON on stdout.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from common import Filters, load_knowledge, utf8_console

utf8_console()

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
K = {}
F = None
DEFAULT_WWR = ["https://weworkremotely.com/categories/remote-programming-jobs.rss",
               "https://weworkremotely.com/categories/remote-management-and-finance-jobs.rss"]


def http(url, data=None, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json", **(headers or {})}
    if data is not None:
        h["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def text(s):
    s = re.sub(r"<p>|<br\s*/?>", "\n", s or "")
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def is_target(title):
    return F.title_ok(title)


def location_ok(where, remote):
    return F.location_ok(where, remote)


def queries():
    s = K.get("search") or {}
    return s.get("board_queries") or [t.split("(")[0].strip().lower() for t in s.get("target_titles", [])[:4]]


# --- Hacker News "Who is hiring?" -------------------------------------------------------------

def hn():
    hits = json.loads(http("https://hn.algolia.com/api/v1/search_by_date?"
                           "tags=story,author_whoishiring&hitsPerPage=10"))["hits"]
    thread = next(h for h in hits if h["title"].lower().startswith("ask hn: who is hiring"))
    item = json.loads(http(f"https://hn.algolia.com/api/v1/items/{thread['objectID']}"))
    out = []
    for c in item.get("children", []):
        body = text(c.get("text"))
        if not body:
            continue
        head = body.split("\n", 1)[0]
        # Posts list several roles ("Company | Role A, Role B | Remote (EU)"); take the first
        # segment in the opening ~600 chars that is itself a target title.
        segs = [re.split(r" [—–-] |: ", seg.strip())[0] for seg in re.split(r"[|\n,;•()]", body[:600])]
        role = next((x for x in segs if len(x) <= 70 and not re.match(r"(i['’]?m|i am|we|our|hiring)\b", x, re.I)
                     and is_target(x)), None)
        if not role:
            continue
        keep, restricted = location_ok(head, "remote" in head.lower())
        if not keep:
            continue
        out.append({"source": "hn", "company": head.split("|")[0].strip()[:80], "title": role[:120],
                    "location": head[:200], "remote_restricted": restricted,
                    "url": f"https://news.ycombinator.com/item?id={c['id']}",
                    "posted": c.get("created_at", "")[:10], "description": body[:600]})
    return out, f'HN thread: {thread["title"]}'


# --- Himalayas --------------------------------------------------------------------------------

def himalayas():
    out, seen = [], set()
    for q in queries():
        d = json.loads(http("https://himalayas.app/jobs/api/search?" +
                            urllib.parse.urlencode({"q": q, "limit": 50})))
        for j in d.get("jobs", []):
            key = j.get("guid") or j.get("applicationLink")
            if key in seen or not is_target(j.get("title")):
                continue
            seen.add(key)
            restr = j.get("locationRestrictions") or []
            where = ", ".join(restr) or "Worldwide"
            keep, restricted = location_ok(where, True)
            if not keep:
                continue
            sal = (f'{j.get("minSalary")}-{j.get("maxSalary")} {j.get("currency") or ""}'.strip()
                   if j.get("minSalary") else None)
            out.append({"source": "himalayas", "company": j.get("companyName"), "title": j.get("title"),
                        "location": where, "remote_restricted": restricted, "salary": sal,
                        "url": j.get("applicationLink"),
                        "posted": time.strftime("%Y-%m-%d", time.gmtime(int(j.get("pubDate") or 0))),
                        "description": text(j.get("excerpt"))[:400]})
        time.sleep(1)
    return out, "Himalayas: " + ", ".join(queries())


# --- Getro (VC portfolio job boards) ----------------------------------------------------------

def getro():
    boards = K.get("vc_boards", [])
    out, seen, notes = [], set(), []
    for b in boards:
        for q in queries():
            try:
                d = json.loads(http(f"https://api.getro.com/api/v2/collections/{b['getro_id']}/search/jobs",
                                    {"hitsPerPage": 50, "page": 0, "filters": {}, "query": q},
                                    {"Origin": f"https://{b['host']}"}))
            except (urllib.error.URLError, OSError) as ex:  # includes timeouts: skip this board only
                notes.append(f'{b["name"]}: {ex}')
                break
            for j in d.get("results", {}).get("jobs", []):
                if j["id"] in seen or not is_target(j.get("title")):
                    continue
                seen.add(j["id"])
                where = "; ".join(j.get("locations") or [])
                keep, restricted = location_ok(where, j.get("work_mode") == "remote")
                if not keep:
                    continue
                sal = None
                if j.get("compensation_public") and j.get("compensation_amount_min_cents"):
                    sal = (f'{j["compensation_amount_min_cents"] // 100}-'
                           f'{(j.get("compensation_amount_max_cents") or 0) // 100} '
                           f'{j.get("compensation_currency") or ""}/{j.get("compensation_period") or ""}')
                out.append({"source": f"getro:{b['name']}", "company": (j.get("organization") or {}).get("name"),
                            "title": j["title"], "location": where or j.get("work_mode"),
                            "work_mode": j.get("work_mode"), "remote_restricted": restricted, "salary": sal,
                            "url": j.get("url"), "posted": time.strftime("%Y-%m-%d", time.gmtime(j.get("created_at", 0)))})
            time.sleep(0.5)
    return out, "; ".join(notes) or f"Getro boards: {', '.join(b['name'] for b in boards)}"


# --- We Work Remotely -------------------------------------------------------------------------

def wwr():
    out = []
    for feed in (K.get("search") or {}).get("wwr_feeds") or DEFAULT_WWR:
        root = ET.fromstring(http(feed, headers={"Accept": "application/rss+xml"}))
        for it in root.iter("item"):
            full = it.findtext("title") or ""
            company, _, title = full.partition(": ")
            if not is_target(title):
                continue
            region = it.findtext("region") or ""
            keep, restricted = location_ok(region or "Anywhere", True)
            if not keep:
                continue
            out.append({"source": "wwr", "company": company, "title": title, "location": region or "Anywhere",
                        "remote_restricted": restricted, "url": it.findtext("link"),
                        "posted": (it.findtext("pubDate") or "")[:16]})
    return out, "We Work Remotely feeds"


SOURCES = {"hn": hn, "himalayas": himalayas, "getro": getro, "wwr": wwr}


def dedupe(jobs):
    """One row per company + title; multi-country postings (one ad per country) merge their locations."""
    out = {}
    for j in jobs:
        key = ((j.get("company") or "").lower().strip(), re.sub(r"\W+", " ", (j.get("title") or "").lower()).strip())
        if key in out:
            prev = out[key]
            locs = {x.strip() for x in f'{prev.get("location") or ""};{j.get("location") or ""}'.split(";") if x.strip()}
            prev["location"] = "; ".join(sorted(locs))
            prev["remote_restricted"] = prev.get("remote_restricted") and j.get("remote_restricted")
            prev["salary"] = prev.get("salary") or j.get("salary")
        else:
            out[key] = dict(j)
    return list(out.values())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", choices=sorted(SOURCES) + ["all"])
    p.add_argument("--include-restricted", action="store_true",
                   help="also keep remote roles tied to places outside your remote rule (flagged)")
    a = p.parse_args()
    global K, F
    K = load_knowledge()
    F = Filters(K, a.include_restricted)
    res = []
    for name in (SOURCES if a.source == "all" else [a.source]):
        try:
            jobs, note = SOURCES[name]()
            print(f"INFO: {note} → {len(jobs)} roles", file=sys.stderr)
            res += jobs
        except Exception as ex:  # one broken source must not kill the sweep
            print(f"WARN: {name} failed: {ex}", file=sys.stderr)
    json.dump(dedupe(res), sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
