"""Shared helpers for the Artemis tools: where the user's profile lives, and the title/location
filters built from it. Stdlib only.

Every personal choice (target titles, where you can work, remote rules) lives in
profile/knowledge.json → "filters", written by `artemis setup`. Nothing about a specific person is
hardcoded here.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROFILE = os.environ.get("ARTEMIS_PROFILE_DIR") or os.path.join(ROOT, "profile")

REMOTE = r"remote|anywhere|distributed|work from home|wfh|home.based"
# Words left over after removing these mean the posting names a place ("Remote, US").
NOISE = REMOTE + r"|[\W\d_]+|full.?time|part.?time|contract|hybrid|onsite|on-site|in.office|office"


def utf8_console():
    """Job titles and descriptions contain characters that Windows' cp1252 console can't print."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def profile_path(*parts):
    return os.path.join(PROFILE, *parts)


def load_knowledge(required=True):
    path = profile_path("knowledge.json")
    if not os.path.exists(path):
        if not required:
            return {}
        sys.exit("No profile/knowledge.json yet. Run `artemis setup`, or copy examples/demo/* into "
                 "profile/ to try Artemis with the demo persona.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Filters:
    """Title and location rules from knowledge.json → filters.

    filters.title_regex          a title must match this (the roles you want)
    filters.scope_regex          ...and this, if set (the field: engineering, design, data...)
    filters.exclude_title_regex  ...and must not match this
    filters.location.onsite_ok_regex     places where on-site/hybrid works for you
    filters.location.remote              true if remote roles are wanted
    filters.location.remote_open_regex   remote wording that includes you ("europe|emea|worldwide")
    filters.location.remote_region_regex remote tied to these places is kept but flagged
                                         `remote_restricted` (often hireable via an EOR: check the ad)
    """

    def __init__(self, knowledge, include_restricted=False, title=None):
        f = knowledge.get("filters") or {}
        self.title = title or f.get("title_regex") or ""
        self.scope = f.get("scope_regex") or ""
        self.exclude = f.get("exclude_title_regex") or ""
        loc = f.get("location") or {}
        self.has_location_rule = bool(loc)
        self.onsite = loc.get("onsite_ok_regex") or ""
        self.remote = loc.get("remote", True)
        self.open = loc.get("remote_open_regex") or r"worldwide|anywhere|global"
        self.region = loc.get("remote_region_regex") or ""
        self.include_restricted = include_restricted
        if not self.title:
            print("WARN: knowledge.json has no filters.title_regex, so every title passes. "
                  "Run `artemis setup` to set your target roles.", file=sys.stderr)

    def title_ok(self, title):
        t = title or ""
        return bool((not self.title or re.search(self.title, t, re.I))
                    and (not self.scope or re.search(self.scope, t, re.I))
                    and not (self.exclude and re.search(self.exclude, t, re.I)))

    def location_ok(self, where, remote=None):
        """Return (keep, restricted)."""
        where = where or ""
        if not self.has_location_rule:
            return True, False
        if remote is None:
            remote = bool(re.search(REMOTE, where, re.I))
        if self.onsite and re.search(self.onsite, where, re.I):
            return True, False
        if not (self.remote and remote):
            return False, False
        if re.search(self.open, where, re.I):
            return True, False
        if self.region and re.search(self.region, where, re.I):
            return True, True
        if not re.sub(NOISE, "", where, flags=re.I):
            return True, False  # bare "Remote": treat as open; the fit check reads the ad
        # Any other named place ("Remote, US") usually means remote inside that country only.
        return (True, True) if self.include_restricted else (False, True)
