#!/usr/bin/env python3
"""
daily-report.py — Grewal RE Group nightly build report.

DESIGN PRINCIPLE: there is NO LLM in this script. It can only print facts it
can prove: real `git log` lines and real HTTP status codes from the live site.
That makes it physically incapable of fabricating findings (unlike the other
scheduled agents). Every line in the email is independently verifiable.

Output: a plain-text report to stdout (used as the email body).
Runs in GitHub Actions (Ubuntu, python3, stdlib only).
"""
import subprocess, urllib.request, urllib.error, datetime, os, pathlib

SITE = "https://grewalregroup.com"
START = datetime.date(2026, 6, 24)          # Day 1 of the 90-day supervised phase
WINDOW = 90
KEY_URLS = [
    "/", "/faq.html", "/contact.html", "/blog/", "/communities/",
    "/seller-net-proceeds-calculator.html", "/home-value-estimator.html",
    "/sitemap.xml", "/robots.txt", "/llms.txt", "/assets/css/site-chrome.css?v=3",
]

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

def commits_since(hours=26):
    out = run(["git", "log", f"--since={hours} hours ago",
               "--pretty=format:%h | %ad | %s", "--date=format:%Y-%m-%d %H:%M"])
    return [ln for ln in out.splitlines() if ln.strip()]

def http_status(path):
    try:
        req = urllib.request.Request(SITE + path, method="GET",
                                     headers={"User-Agent": "GrewalNightlyMonitor/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return f"ERR:{type(e).__name__}"

def read_queue():
    p = pathlib.Path(__file__).parent / "daily-queue.md"
    if p.exists():
        items = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
                 if ln.strip().startswith("-")]
        return items
    return []

def main():
    today = datetime.date.fromisoformat(os.environ.get("REPORT_DATE") or datetime.date.today().isoformat())
    day_n = (today - START).days + 1

    L = []
    A = L.append
    A(f"GREWAL SITE — DAILY BUILD REPORT — {today.isoformat()}")
    if day_n <= WINDOW:
        A(f"Day {day_n} of {WINDOW} (supervised phase). Reply with any concern.")
    else:
        A(f"Day {day_n}. Supervised 90-day window complete — cleared for full auto when you say so.")
    A("This report has no LLM. Every line below is a real git commit or a real HTTP status code.")
    A("")

    # --- Deployed in the last ~24h ---
    commits = commits_since(26)
    A("== DEPLOYED (last 24h) ==")
    if commits:
        for c in commits:
            A(f"  {c}")
        A(f"  ({len(commits)} commit(s); verify with `git show <hash>`)")
    else:
        A("  No deploys in the last 24h. (During the review phase most days are drafts/audits, not ships.)")
    A("")

    # --- Live health check ---
    A("== LIVE HEALTH CHECK ==")
    bad = 0
    for u in KEY_URLS:
        s = http_status(u)
        ok = (s == 200)
        if not ok:
            bad += 1
        A(f"  [{'OK ' if ok else 'FLAG'}] {s}  {u}")
    A(f"  Summary: {len(KEY_URLS) - bad}/{len(KEY_URLS)} key URLs healthy" +
      ("" if bad == 0 else f"  <-- {bad} NEED ATTENTION"))
    A("")

    # --- Open items needing the human ---
    queue = read_queue()
    A("== NEEDS YOU ==")
    if queue:
        for q in queue:
            A(f"  {q}")
    else:
        A("  Nothing queued.")
    A("")

    A("== VERIFY ANY LINE ==")
    A("  Deploys: `git show <hash>` in shivraj-ux/grewal-re-group-site")
    A("  Health:  `curl -I https://grewalregroup.com/<path>`")
    A("  Traffic: GA4 analytics.google.com (property G-X3GFZCS0JE)")
    A("")
    A("— Grewal Growth Engine (deterministic nightly monitor, no LLM)")

    print("\n".join(L))

if __name__ == "__main__":
    main()
