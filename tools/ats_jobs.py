#!/usr/bin/env python3
"""Company careers-board scanner: Greenhouse, Lever, Ashby, SmartRecruiters, Workable, Workday.
Stdlib only.

These are the public JSON APIs behind companies' own careers pages, so the data is fresher and
more complete than aggregators, and nothing is scraped.

  python tools/ats_jobs.py scan                         # every company in your watchlist
  python tools/ats_jobs.py scan --company gitlab        # one watchlist entry
  python tools/ats_jobs.py probe greenhouse gitlab      # test a slug before adding it
  python tools/ats_jobs.py probe workday adobe/wd5/external_experienced   # slug = tenant/wdN/site
  python tools/ats_jobs.py scan --title "staff|principal" --location "remote|lisbon"

The watchlist lives in profile/knowledge.json → watchlist:
  {"company": "GitLab", "ats": "greenhouse", "slug": "gitlab", "why": "..."}
Title and location rules come from knowledge.json → filters (see tools/common.py).
Output is JSON on stdout: one object per matching role.
"""
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request

from common import REMOTE, Filters, load_knowledge, utf8_console

utf8_console()


def get(url, data=None):
    req = urllib.request.Request(url, data=data, headers={
        "User-Agent": "Mozilla/5.0", "Accept": "application/json",
        **({"Content-Type": "application/json"} if data else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def strip(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def greenhouse(slug, **_):
    for j in get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")["jobs"]:
        yield {"title": j["title"], "location": (j.get("location") or {}).get("name"),
               "url": j["absolute_url"], "updated": j.get("updated_at"),
               "description": strip(j.get("content"))}


def lever(slug, **_):
    for j in get(f"https://api.lever.co/v0/postings/{slug}?mode=json"):
        c = j.get("categories") or {}
        yield {"title": j["text"], "location": c.get("location"), "team": c.get("team"),
               "workplace": j.get("workplaceType"), "url": j["hostedUrl"],
               "updated": j.get("createdAt"), "description": j.get("descriptionPlain")}


def ashby(slug, **_):
    d = get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
    for j in d.get("jobs", []):
        comp = (j.get("compensation") or {}).get("compensationTierSummary")
        # Many remote roles list the countries they hire in as secondaryLocations, so the primary
        # location alone would drop them.
        locs = [j.get("location")] + [s.get("location") for s in j.get("secondaryLocations") or []]
        where = "; ".join(dict.fromkeys(l for l in locs if l))
        # Ashby's isRemote is set on many office-based roles too: confirm in the JD.
        yield {"title": j["title"], "location": where, "team": j.get("department"),
               "workplace": "remote" if j.get("isRemote") else j.get("workplaceType"),
               "url": j.get("jobUrl"), "updated": j.get("publishedAt"), "salary": comp,
               "description": j.get("descriptionPlain")}


def smartrecruiters(slug, **_):
    d = get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100")
    for j in d.get("content", []):
        loc = j.get("location") or {}
        yield {"title": j["name"], "location": ", ".join(x for x in (loc.get("city"), loc.get("country")) if x),
               "workplace": "remote" if loc.get("remote") else None,
               "url": f"https://jobs.smartrecruiters.com/{slug}/{j['id']}", "updated": j.get("releasedDate"),
               "description": None}


def workable(slug, **_):
    d = get(f"https://apply.workable.com/api/v1/widget/accounts/{slug}")
    for j in d.get("jobs", []):
        yield {"title": j["title"], "location": ", ".join(x for x in (j.get("city"), j.get("country")) if x),
               "workplace": "remote" if j.get("telecommuting") else None,
               "url": j.get("url") or j.get("shortlink"), "updated": j.get("published_on"),
               "description": None}


def workday(slug, search="", cap=200, title_ok=None, **_):
    """slug = tenant/wdN/site, from the careers URL https://<tenant>.<wdN>.myworkdayjobs.com/<site>.
    Workday has no 'all jobs' feed, so we page through a keyword search (the title filter runs after)."""
    tenant, wd, site = slug.split("/")
    base = f"https://{tenant}.{wd}.myworkdayjobs.com"
    for offset in range(0, cap, 20):
        d = get(f"{base}/wday/cxs/{tenant}/{site}/jobs",
                json.dumps({"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": search}).encode())
        posts = d.get("jobPostings", [])
        for j in posts:
            loc = j.get("locationsText")
            if loc and re.fullmatch(r"\d+ Locations", loc) and (title_ok is None or title_ok(j["title"])):
                # Workday collapses multi-city roles to "N Locations"; the detail call has the list.
                try:
                    info = get(f"{base}/wday/cxs/{tenant}/{site}{j.get('externalPath', '')}")["jobPostingInfo"]
                    loc = "; ".join([info.get("location") or ""] + (info.get("additionalLocations") or []))
                except (urllib.error.URLError, KeyError, ValueError):
                    pass
            yield {"title": j["title"], "location": loc,
                   "url": f"{base}/{site}{j.get('externalPath', '')}", "updated": j.get("postedOn"),
                   "description": None}
        if len(posts) < 20:
            break


ATS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby,
       "smartrecruiters": smartrecruiters, "workable": workable, "workday": workday}


def match(company, jobs, filters, loc_re=None, exclude_loc=None, full=False):
    """Apply the title and location rules to one company's postings."""
    out = []
    for j in jobs:
        where = " ".join(str(x) for x in (j.get("location"), j.get("workplace")) if x)
        if not filters.title_ok(j["title"]):
            continue
        if loc_re:
            if not re.search(loc_re, where, re.I):
                continue
        elif re.fullmatch(r"\d+ Locations", where.strip(), re.I):
            j["remote_restricted"] = None  # Workday hides multi-location lists: open the ad
        else:
            keep, restricted = filters.location_ok(where, bool(re.search(REMOTE, where, re.I)))
            if not keep:
                continue
            j["remote_restricted"] = restricted
        if exclude_loc and re.search(exclude_loc, where, re.I):
            continue
        if not full:
            j["description"] = (j.get("description") or "")[:400] or None
        out.append({"company": company, **j})
    return out


def scan(entries, filters, loc_re=None, exclude_loc=None, full=False, workday_search=""):
    out, errors = [], []
    for e in entries:
        try:
            jobs = ATS[e["ats"]](e["slug"], search=workday_search, title_ok=filters.title_ok)
            out += match(e["company"], jobs, filters, loc_re, exclude_loc, full)
        except (urllib.error.URLError, KeyError, ValueError) as ex:
            errors.append(f'{e["company"]} ({e["ats"]}/{e["slug"]}): {ex}')
    for err in errors:
        print("WARN:", err, file=sys.stderr)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--company", help="only this watchlist company (case-insensitive substring)")
    s.add_argument("--title", help="title regex; overrides filters.title_regex for this run")
    s.add_argument("--location", default=None,
                   help="location/workplace regex; default = your rule in knowledge.json → filters.location")
    s.add_argument("--exclude-location", default=None, help="drop roles whose location matches this regex")
    s.add_argument("--include-restricted", action="store_true",
                   help="also keep remote roles tied to places outside your remote rule (flagged)")
    s.add_argument("--full", action="store_true", help="include full descriptions")
    pr = sub.add_parser("probe")
    pr.add_argument("ats", choices=sorted(ATS))
    pr.add_argument("slug")
    a = p.parse_args()
    if a.cmd == "probe":
        try:
            jobs = list(ATS[a.ats](a.slug))
            res = {"ats": a.ats, "slug": a.slug, "open_roles": len(jobs), "sample": [j["title"] for j in jobs[:10]]}
        except urllib.error.HTTPError as ex:
            res = {"ats": a.ats, "slug": a.slug, "error": f"HTTP {ex.code}: wrong slug or not on this ATS"}
    else:
        k = load_knowledge()
        wl = k.get("watchlist", [])
        if not wl:
            print("WARN: the watchlist is empty. Add companies with `artemis watch add <company>`.", file=sys.stderr)
        if a.company:
            wl = [e for e in wl if a.company.lower() in e["company"].lower()]
        f = Filters(k, a.include_restricted, a.title)
        res = scan(wl, f, a.location, a.exclude_location, a.full,
                   (k.get("filters") or {}).get("workday_search", ""))
    json.dump(res, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
