#!/usr/bin/env python3
"""
send-report.py — emails report.txt via the Resend API (no SMTP, no app password).
Reads RESEND_API_KEY from the environment. Run after daily-report.py has written
report.txt. Used by .github/workflows/nightly-report.yml.
"""
import json, os, sys, datetime, urllib.request, urllib.error

key = os.environ.get("RESEND_API_KEY")
if not key:
    print("ERROR: RESEND_API_KEY secret is not set. Add it in GitHub repo Settings -> "
          "Secrets and variables -> Actions.")
    sys.exit(1)

try:
    body = open("report.txt", encoding="utf-8").read()
except FileNotFoundError:
    print("ERROR: report.txt not found (did daily-report.py run first?)")
    sys.exit(1)

subject = f"Grewal Site - Daily Build Report - {datetime.date.today().isoformat()}"

payload = {
    # In Resend test mode (no verified domain) the 'from' MUST be onboarding@resend.dev
    # and 'to' MUST be the email you signed up with. After you verify grewalregroup.com,
    # switch 'from' to e.g. reports@grewalregroup.com and add the 2nd address to 'to'.
    "from": "Grewal Growth Engine <onboarding@resend.dev>",
    "to": ["shivraj@grewalregroup.com"],
    "subject": subject,
    "text": body,
}

req = urllib.request.Request(
    "https://api.resend.com/emails",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("Resend OK:", r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print("Resend ERROR:", e.code, e.read().decode())
    sys.exit(1)
