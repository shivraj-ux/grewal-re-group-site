#!/usr/bin/env python3
"""
Grewal RE Group — SEO Analytics Agent (read-only monitor)

Pulls performance data and writes a report. Does NOT modify site content;
content refresh/creation is handled by daily_agent.py (PR-based).

Cadence (see .github/workflows/seo-agent.yml):
  - Weekly (Monday): full report + page-2 opportunities + keyword tracking.

Data sources:
  1. Google Search Console  — rankings, clicks, CTR, impressions (the truth source)
  2. Google Analytics 4     — traffic, channels, engagement, conversions
  3. PageSpeed Insights      — Core Web Vitals for key pages

Outputs:
  - logs/seo/report-YYYY-MM-DD.md   (human-readable weekly report)
  - data/seo/latest-insights.json   (machine-readable; feeds the content agent)
  - /tmp/seo-pr-body.md             (PR description)

Auth: service account JSON in env GA_SERVICE_ACCOUNT_JSON.
The service-account email must be granted:
  - GA4 Admin -> Property Access Management -> Viewer
  - Search Console -> Settings -> Users and permissions -> Restricted/Full
Property targets (not secret) come from env, falling back to data/seo-config.json:
  - GA4_PROPERTY_ID   e.g. "properties/123456789" or just "123456789"
  - GSC_SITE_URL      e.g. "https://grewalregroup.com/" or "sc-domain:grewalregroup.com"
Optional: PAGESPEED_API_KEY (raises PSI rate limits).

Every section degrades gracefully: a missing credential or un-granted access is
logged and skipped, never fatal — so a partial run still produces a useful report.
"""

import json
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ─── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SEO_DATA_DIR = DATA_DIR / "seo"
LOGS_DIR = ROOT / "logs" / "seo"
CONFIG_PATH = DATA_DIR / "seo-config.json"
PR_BODY_PATH = Path("/tmp/seo-pr-body.md")

CST = timezone(timedelta(hours=-6))
TODAY = datetime.now(tz=CST).strftime("%Y-%m-%d")
TODAY_DISPLAY = datetime.now(tz=CST).strftime("%B %-d, %Y")

GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"

errors = []
notes = []


def log_error(step, error):
    errors.append({"step": step, "error": str(error)})
    print(f"ERROR [{step}]: {error}", file=sys.stderr)


def log_note(msg):
    notes.append(msg)
    print(f"NOTE: {msg}")


# ─── Config & credentials ─────────────────────────────────────────────────────
def load_config():
    cfg = json.loads(CONFIG_PATH.read_text())
    # env overrides (set these as GitHub repo Variables, not secrets)
    prop = os.environ.get("GA4_PROPERTY_ID", "").strip() or cfg.get("ga4_property_id", "")
    if prop and not prop.startswith("properties/"):
        prop = f"properties/{prop}"
    cfg["ga4_property_id"] = prop
    cfg["gsc_site_url"] = (
        os.environ.get("GSC_SITE_URL", "").strip() or cfg.get("gsc_site_url", "")
    )
    return cfg


def load_credentials(scopes):
    raw = os.environ.get("GA_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw:
        raise RuntimeError("GA_SERVICE_ACCOUNT_JSON is not set")
    from google.oauth2 import service_account  # imported lazily

    info = json.loads(raw)
    return service_account.Credentials.from_service_account_info(info, scopes=scopes)


def date_range(days_back, offset=0):
    end = datetime.now(tz=CST).date() - timedelta(days=1 + offset)
    start = end - timedelta(days=days_back - 1)
    return start.isoformat(), end.isoformat()


# ─── Google Search Console ─────────────────────────────────────────────────────
def pull_gsc(cfg):
    """Return rankings/clicks/impressions + page-2 opportunities + keyword tracking."""
    from googleapiclient.discovery import build

    site = cfg["gsc_site_url"]
    creds = load_credentials([GSC_SCOPE])
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    start, end = date_range(cfg["lookback_days"])

    def query(dimensions, row_limit=250):
        body = {"startDate": start, "endDate": end, "dimensions": dimensions,
                "rowLimit": row_limit}
        return svc.searchanalytics().query(siteUrl=site, body=body).execute().get("rows", [])

    out = {"period": f"{start} to {end}", "site": site}

    # Totals
    totals = svc.searchanalytics().query(
        siteUrl=site, body={"startDate": start, "endDate": end}
    ).execute()
    t = (totals.get("rows") or [{}])[0]
    out["totals"] = {
        "clicks": t.get("clicks", 0), "impressions": t.get("impressions", 0),
        "ctr": round(t.get("ctr", 0) * 100, 2), "position": round(t.get("position", 0), 1),
    }

    # Top queries & pages
    out["top_queries"] = [
        {"query": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
         "ctr": round(r["ctr"] * 100, 1), "position": round(r["position"], 1)}
        for r in query(["query"])
    ][:25]
    out["top_pages"] = [
        {"page": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
         "position": round(r["position"], 1)}
        for r in query(["page"])
    ][:25]

    # Page-2 opportunities: position 10.5–20 with real impressions = closest to page 1
    min_imp = cfg.get("page2_min_impressions", 30)
    out["page2_opportunities"] = sorted(
        [q for q in [
            {"query": r["keys"][0], "impressions": r["impressions"],
             "position": round(r["position"], 1), "clicks": r["clicks"]}
            for r in query(["query"])]
         if 10.5 <= q["position"] <= 20.5 and q["impressions"] >= min_imp],
        key=lambda x: (-x["impressions"], x["position"]),
    )[:20]

    # Priority-keyword tracking: match config keywords against returned queries
    q_by_text = {r["keys"][0].lower(): r for r in query(["query"], row_limit=2000)}
    tracked = []
    for kw in cfg["priority_keywords"]:
        r = q_by_text.get(kw.lower())
        tracked.append({
            "keyword": kw,
            "position": round(r["position"], 1) if r else None,
            "impressions": r["impressions"] if r else 0,
            "clicks": r["clicks"] if r else 0,
            "status": "not ranking / no impressions" if not r else (
                "page 1" if r["position"] <= 10 else
                "page 2" if r["position"] <= 20 else "page 3+"),
        })
    out["priority_keywords"] = tracked
    return out


# ─── Google Analytics 4 ────────────────────────────────────────────────────────
def pull_ga4(cfg):
    prop = cfg["ga4_property_id"]
    if not prop:
        raise RuntimeError("GA4_PROPERTY_ID not configured")
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest, OrderBy,
    )

    creds = load_credentials([GA4_SCOPE])
    client = BetaAnalyticsDataClient(credentials=creds)
    start, end = date_range(cfg["lookback_days"])
    dr = [DateRange(start_date=start, end_date=end)]
    out = {"period": f"{start} to {end}"}

    # Top-line metrics
    rep = client.run_report(RunReportRequest(
        property=prop, date_ranges=dr,
        metrics=[Metric(name=m) for m in
                 ("sessions", "totalUsers", "newUsers", "engagementRate",
                  "averageSessionDuration", "conversions")],
    ))
    if rep.rows:
        vals = [v.value for v in rep.rows[0].metric_values]
        out["totals"] = {
            "sessions": int(float(vals[0])), "users": int(float(vals[1])),
            "new_users": int(float(vals[2])), "engagement_rate": round(float(vals[3]) * 100, 1),
            "avg_session_sec": round(float(vals[4]), 1), "conversions": int(float(vals[5])),
        }

    # Traffic by channel
    rep = client.run_report(RunReportRequest(
        property=prop, date_ranges=dr,
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name="sessions"), Metric(name="conversions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    ))
    out["channels"] = [
        {"channel": r.dimension_values[0].value,
         "sessions": int(float(r.metric_values[0].value)),
         "conversions": int(float(r.metric_values[1].value))}
        for r in rep.rows
    ]

    # Top landing pages
    rep = client.run_report(RunReportRequest(
        property=prop, date_ranges=dr,
        dimensions=[Dimension(name="landingPagePlusQueryString")],
        metrics=[Metric(name="sessions"), Metric(name="conversions")],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=20,
    ))
    out["top_landing_pages"] = [
        {"page": r.dimension_values[0].value,
         "sessions": int(float(r.metric_values[0].value)),
         "conversions": int(float(r.metric_values[1].value))}
        for r in rep.rows
    ]
    return out


# ─── PageSpeed Insights ────────────────────────────────────────────────────────
def pull_psi(cfg):
    key = os.environ.get("PAGESPEED_API_KEY", "").strip()
    results = []
    for url in cfg.get("psi_pages", []):
        params = {"url": url, "strategy": "mobile", "category": "PERFORMANCE"}
        if key:
            params["key"] = key
        try:
            r = requests.get(
                "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                params=params, timeout=90)
            r.raise_for_status()
            d = r.json()
            lh = d.get("lighthouseResult", {})
            audits = lh.get("audits", {})
            results.append({
                "url": url,
                "performance": round(lh.get("categories", {}).get("performance", {})
                                     .get("score", 0) * 100),
                "lcp": audits.get("largest-contentful-paint", {}).get("displayValue"),
                "cls": audits.get("cumulative-layout-shift", {}).get("displayValue"),
                "tbt": audits.get("total-blocking-time", {}).get("displayValue"),
            })
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return results


# ─── Report rendering ──────────────────────────────────────────────────────────
def render_report(gsc, ga4, psi):
    L = [f"# Grewal RE Group — Weekly SEO Report", f"_{TODAY_DISPLAY}_", ""]

    L.append("## Search Console (organic search)")
    if gsc:
        t = gsc["totals"]
        L += [f"_Period: {gsc['period']}_", "",
              f"- **Clicks:** {t['clicks']}  |  **Impressions:** {t['impressions']}  "
              f"|  **CTR:** {t['ctr']}%  |  **Avg position:** {t['position']}", ""]
        L.append("### 🎯 Page-2 opportunities (closest to page 1 — prioritize these)")
        if gsc["page2_opportunities"]:
            L.append("| Query | Position | Impressions | Clicks |")
            L.append("|---|---|---|---|")
            for q in gsc["page2_opportunities"]:
                L.append(f"| {q['query']} | {q['position']} | {q['impressions']} | {q['clicks']} |")
        else:
            L.append("_None in the 11–20 band yet (normal for a young domain — keep building)._")
        L.append("")
        L.append("### Priority keyword tracking")
        L.append("| Keyword | Position | Status | Impr |")
        L.append("|---|---|---|---|")
        for k in gsc["priority_keywords"]:
            pos = k["position"] if k["position"] is not None else "—"
            L.append(f"| {k['keyword']} | {pos} | {k['status']} | {k['impressions']} |")
        L.append("")
        L.append("### Top queries")
        L.append("| Query | Clicks | Impr | CTR | Pos |")
        L.append("|---|---|---|---|---|")
        for q in gsc["top_queries"][:15]:
            L.append(f"| {q['query']} | {q['clicks']} | {q['impressions']} | {q['ctr']}% | {q['position']} |")
    else:
        L.append("_No GSC data — check that the service account is added under "
                 "Search Console → Settings → Users and permissions, and GSC_SITE_URL is set._")
    L.append("")

    L.append("## Analytics 4 (traffic & conversions)")
    if ga4:
        t = ga4.get("totals", {})
        L += [f"_Period: {ga4['period']}_", "",
              f"- **Sessions:** {t.get('sessions')}  |  **Users:** {t.get('users')}  "
              f"|  **Engagement rate:** {t.get('engagement_rate')}%  "
              f"|  **Conversions:** {t.get('conversions')}", ""]
        if ga4.get("channels"):
            L.append("### Sessions by channel")
            L.append("| Channel | Sessions | Conversions |")
            L.append("|---|---|---|")
            for c in ga4["channels"]:
                L.append(f"| {c['channel']} | {c['sessions']} | {c['conversions']} |")
            L.append("")
        if ga4.get("top_landing_pages"):
            L.append("### Top landing pages")
            L.append("| Page | Sessions | Conversions |")
            L.append("|---|---|---|")
            for p in ga4["top_landing_pages"][:12]:
                L.append(f"| {p['page']} | {p['sessions']} | {p['conversions']} |")
    else:
        L.append("_No GA4 data — check that the service account is a Viewer under "
                 "GA4 Admin → Property Access Management, and GA4_PROPERTY_ID is set._")
    L.append("")

    L.append("## Core Web Vitals (PageSpeed, mobile)")
    if psi:
        L.append("| Page | Perf | LCP | CLS | TBT |")
        L.append("|---|---|---|---|---|")
        for p in psi:
            if "error" in p:
                L.append(f"| {p['url']} | error | | | |")
            else:
                L.append(f"| {p['url']} | {p['performance']} | {p.get('lcp')} | "
                         f"{p.get('cls')} | {p.get('tbt')} |")
    else:
        L.append("_No PageSpeed data this run._")
    L.append("")

    if errors:
        L.append("## ⚠️ Run issues")
        for e in errors:
            L.append(f"- **{e['step']}**: {e['error']}")
        L.append("")

    return "\n".join(L)


def main():
    print(f"=== SEO Analytics Agent — {TODAY} ===")
    SEO_DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    cfg = load_config()

    gsc = ga4 = None
    try:
        gsc = pull_gsc(cfg)
    except Exception as e:
        log_error("search-console", e)
        traceback.print_exc()
    try:
        ga4 = pull_ga4(cfg)
    except Exception as e:
        log_error("analytics-4", e)
        traceback.print_exc()
    try:
        psi = pull_psi(cfg)
    except Exception as e:
        log_error("pagespeed", e)
        psi = None

    insights = {"generated": TODAY, "gsc": gsc, "ga4": ga4, "psi": psi, "errors": errors}
    (SEO_DATA_DIR / "latest-insights.json").write_text(json.dumps(insights, indent=2))

    report = render_report(gsc, ga4, psi)
    report_path = LOGS_DIR / f"report-{TODAY}.md"
    report_path.write_text(report)
    (LOGS_DIR / "latest.md").write_text(report)
    print(f"Wrote {report_path}")

    n_opp = len(gsc["page2_opportunities"]) if gsc else 0
    PR_BODY_PATH.write_text(
        f"## Weekly SEO Report — {TODAY_DISPLAY}\n\n"
        f"Automated read-only analytics pull (GSC + GA4 + PageSpeed).\n\n"
        f"- Page-2 opportunities found: **{n_opp}**\n"
        f"- Full report: `logs/seo/report-{TODAY}.md`\n"
        f"- Machine insights: `data/seo/latest-insights.json`\n\n"
        + ("⚠️ Some sources failed — see the report's *Run issues* section "
           "(usually means the service account hasn't been granted access yet).\n"
           if errors else "All data sources returned successfully.\n")
    )
    # Non-fatal exit even with partial errors, so the workflow can still open the PR.
    print("Done." + (f" ({len(errors)} source(s) had issues)" if errors else ""))


if __name__ == "__main__":
    main()
