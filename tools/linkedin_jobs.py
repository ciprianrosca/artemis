#!/usr/bin/env python3
"""LinkedIn public (logged-out) job search + job detail, stdlib only.

Uses the same guest endpoints the public linkedin.com/jobs page calls. No login, no cookies,
no account at risk. Low volume on purpose: small page counts, a pause between requests, and a
hard stop on HTTP 429. This is for one person's job search, not bulk collection.

  python tools/linkedin_jobs.py search "Senior Backend Engineer" --location "Portugal" --days 7
  python tools/linkedin_jobs.py search "Staff Engineer" --location "European Union" --remote --level mid-senior
  python tools/linkedin_jobs.py detail 4470145913
  python tools/linkedin_jobs.py profile <slug-or-url>   # a public profile (yours, a hiring manager's)

Without --location, the first entry of knowledge.json → search.linkedin_locations is used.

Output is JSON on stdout.
"""
import argparse
import html
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from common import load_knowledge, utf8_console

utf8_console()

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}"

TIME = {1: "r86400", 7: "r604800", 30: "r2592000"}
WORKPLACE = {"onsite": "1", "remote": "2", "hybrid": "3"}
LEVEL = {"internship": "1", "entry": "2", "associate": "3", "mid-senior": "4",
         "director": "5", "executive": "6"}


class RateLimited(Exception):
    pass


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise RateLimited()
        if e.code in (400, 404):
            return ""
        raise


def clean(s):
    s = re.sub(r"<br\s*/?>", "\n", s or "")
    s = re.sub(r"</(p|li|ul|ol|h\d)>", "\n", s)
    s = re.sub(r"<li[^>]*>", "- ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", s).strip()


def first(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return clean(m.group(1)) if m else None


def parse_cards(page):
    jobs = []
    for card in re.split(r"<li>", page)[1:]:
        jid = first(r'urn:li:jobPosting:(\d+)', card)
        if not jid:
            continue
        url = first(r'class="base-card__full-link[^"]*"[^>]*href="([^"?]+)', card)
        jobs.append({
            "id": jid,
            "title": first(r'base-search-card__title">(.*?)</h3>', card),
            "company": first(r'base-search-card__subtitle">(.*?)</h4>', card),
            "location": first(r'job-search-card__location">(.*?)</span>', card),
            "posted": first(r'<time[^>]*datetime="([^"]+)"', card),
            "salary": first(r'job-search-card__salary-info">(.*?)</span>', card),
            "url": url or f"https://www.linkedin.com/jobs/view/{jid}",
        })
    return jobs


def search(a):
    params = {"keywords": a.keywords, "location": a.location, "start": 0}
    if a.days:
        params["f_TPR"] = TIME.get(a.days, f"r{a.days * 86400}")
    wt = [WORKPLACE[k] for k in ("onsite", "remote", "hybrid") if getattr(a, k)]
    if wt:
        params["f_WT"] = ",".join(wt)
    if a.level:
        params["f_E"] = ",".join(LEVEL[l.strip()] for l in a.level.split(","))
    if a.geo_id:
        params["geoId"] = a.geo_id
    seen, out = set(), []
    for page in range(a.pages):
        params["start"] = page * 10
        try:
            body = fetch(SEARCH_URL + "?" + urllib.parse.urlencode(params))
        except RateLimited:
            print("WARN: LinkedIn returned 429 — stopped early. Wait before retrying.", file=sys.stderr)
            break
        cards = parse_cards(body)
        if not cards:
            break
        for c in cards:
            if c["id"] not in seen:
                seen.add(c["id"])
                out.append(c)
        time.sleep(random.uniform(2.0, 4.0))
    return out


def detail(job_id):
    body = fetch(DETAIL_URL.format(id=job_id))
    if not body:
        return {"id": job_id, "error": "not found (expired or removed)"}
    criteria = dict(zip(
        [clean(x) for x in re.findall(r'job-criteria-subheader">(.*?)</h3>', body, re.S)],
        [clean(x) for x in re.findall(r'job-criteria-text[^"]*">(.*?)</span>', body, re.S)],
    ))
    return {
        "id": job_id,
        "url": f"https://www.linkedin.com/jobs/view/{job_id}",
        "title": first(r'topcard__title">(.*?)</h2>', body),
        "company": first(r'topcard__org-name-link[^>]*>(.*?)</a>', body),
        "location": first(r'topcard__flavor--bullet">(.*?)</span>', body),
        "posted": first(r'posted-time-ago__text[^>]*>(.*?)</span>', body),
        "applicants": first(r'num-applicants__caption[^>]*>(.*?)</(?:figcaption|span)>', body),
        "salary": first(r'salary compensation__salary">(.*?)</div>', body),
        "criteria": criteria,
        "description": first(r'show-more-less-html__markup[^>]*>(.*?)</div>', body),
    }


def section(body, name):
    m = re.search(r'<section[^>]*data-section="%s"[^>]*>(.*?)</section>' % name, body, re.S)
    if not m:
        return None
    t = re.sub(r'\*\]:[^>]*>', " ", m.group(1))  # drop Tailwind selector debris the guest page leaks
    return clean(t)


def profile(slug):
    """Public (logged-out) profile: JSON-LD Person block + visible sections. What a recruiter sees
    without logging in, which is exactly what matters for the candidate's own profile."""
    slug = re.sub(r"^.*/in/", "", slug).strip("/")
    body = fetch(f"https://www.linkedin.com/in/{slug}/")
    if not body or "authwall" in body[:5000]:
        return {"slug": slug, "error": "not public (authwall) or not found"}
    person = {}
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            d = json.loads(blob)
        except ValueError:
            continue
        for x in d.get("@graph", [d]):
            if x.get("@type") == "Person":
                person = x
    roles = []
    for org in person.get("worksFor", []) + person.get("alumniOf", []):
        m = org.get("member") or {}
        roles.append({"org": org.get("name"), "type": org.get("@type"), "location": org.get("location"),
                      "start": m.get("startDate"), "end": m.get("endDate"),
                      "description": clean(m.get("description"))})
    return {
        "slug": slug,
        "url": f"https://www.linkedin.com/in/{slug}/",
        "name": person.get("name"),
        "headline": first(r"<title>(.*?) \| LinkedIn</title>", body),
        "job_title": person.get("jobTitle"),
        "about": clean(person.get("description")),
        "location": (person.get("address") or {}).get("addressLocality"),
        "roles": roles,
        "experience_titles": section(body, "experience"),
        **{k: section(body, k) for k in ("projects", "volunteering", "courses", "certifications",
                                         "languages", "honors-and-awards", "recommendations")},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("keywords")
    s.add_argument("--location", help="free text: a country, city or region")
    s.add_argument("--geo-id", help="LinkedIn geoId, overrides fuzzy location matching")
    s.add_argument("--days", type=int, default=7, help="posted within N days (1/7/30 map to LinkedIn presets)")
    s.add_argument("--remote", action="store_true")
    s.add_argument("--hybrid", action="store_true")
    s.add_argument("--onsite", action="store_true")
    s.add_argument("--level", help="comma list: mid-senior,director,executive")
    s.add_argument("--pages", type=int, default=3, help="10 results per page; keep small")
    d = sub.add_parser("detail")
    d.add_argument("ids", nargs="+")
    pf = sub.add_parser("profile")
    pf.add_argument("slug", help="profile slug or full linkedin.com/in/... URL")
    a = p.parse_args()
    if a.cmd == "profile":
        res = profile(a.slug)
    elif a.cmd == "search":
        if not a.location:
            locs = (load_knowledge(required=False).get("search") or {}).get("linkedin_locations") or []
            if not locs:
                sys.exit("Pass --location, or set search.linkedin_locations in profile/knowledge.json.")
            a.location = locs[0]
        res = search(a)
    else:
        res = []
        for i, jid in enumerate(a.ids):
            if i:
                time.sleep(random.uniform(2.0, 4.0))
            try:
                res.append(detail(jid))
            except RateLimited:
                print("WARN: 429 — stopped early.", file=sys.stderr)
                break
        res = res[0] if len(res) == 1 else res
    json.dump(res, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
