#!/usr/bin/env python3
"""Scan the shared company catalog (data/catalog.json, ~1,000 tech companies on Greenhouse, Lever,
Ashby and Workable) with your title and location rules. Use it to find companies you didn't know
to look at, then add the good ones to your watchlist. Stdlib only.

  python tools/discover.py                    # the whole catalog, 16 boards at a time
  python tools/discover.py --ats ashby        # one ATS only
  python tools/discover.py --skip-watchlist   # leave out companies already on your watchlist

Slugs in the catalog are unverified: boards that fail are skipped quietly. Takes a few minutes.
Output is JSON on stdout, one object per matching role, with the ats and slug so a hit can go
straight into the watchlist.
"""
import argparse
import json
import os
import socket
import sys
from concurrent.futures import ThreadPoolExecutor

from ats_jobs import ATS, match
from common import ROOT, Filters, load_knowledge, utf8_console

utf8_console()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ats", choices=["ashby", "greenhouse", "lever", "workable"])
    p.add_argument("--skip-watchlist", action="store_true")
    p.add_argument("--include-restricted", action="store_true")
    p.add_argument("--workers", type=int, default=16)
    a = p.parse_args()

    k = load_knowledge()
    f = Filters(k, a.include_restricted)
    with open(os.path.join(ROOT, "data", "catalog.json"), encoding="utf-8") as fh:
        catalog = {ats: slugs for ats, slugs in json.load(fh).items() if not ats.startswith("_")}
    watched = {(e["ats"], e["slug"]) for e in k.get("watchlist", [])} if a.skip_watchlist else set()
    pairs = [(ats, s) for ats, slugs in catalog.items() if not a.ats or ats == a.ats
             for s in dict.fromkeys(slugs) if (ats, s) not in watched]

    socket.setdefaulttimeout(15)

    def fetch(pair):
        try:
            return pair, list(ATS[pair[0]](pair[1]))
        except Exception:  # unverified slug: skip
            return pair, []

    print(f"INFO: scanning {len(pairs)} boards…", file=sys.stderr)
    out, live = [], 0
    with ThreadPoolExecutor(a.workers) as ex:
        for (ats, slug), jobs in ex.map(fetch, pairs):
            live += bool(jobs)
            for j in match(slug, jobs, f):
                out.append({"ats": ats, "slug": slug, **j})
    print(f"INFO: {live} boards answered, {len(out)} matching roles", file=sys.stderr)
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
