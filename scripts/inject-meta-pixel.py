#!/usr/bin/env python3
"""
Sitewide Meta (Facebook) Pixel install.

Inserts the standard Meta Pixel <script> block right after the opening
<head> tag, and the <noscript> fallback <img> right after the opening
<body> tag, on every public HTML page.

Idempotent: any file that already contains the pixel ID is skipped, so
re-running is a no-op on already-patched files.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PIXEL_ID = "1325923113044966"

PIXEL_SCRIPT = f"""<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{PIXEL_ID}');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->
"""

NOSCRIPT_FALLBACK = f'''<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id={PIXEL_ID}&ev=PageView&noscript=1"
/></noscript>
'''

HEAD_RE = re.compile(r"(<head[^>]*>\n)")
BODY_RE = re.compile(r"(<body[^>]*>\n)")


def patch(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if PIXEL_ID in html:
        return False

    if not HEAD_RE.search(html) or not BODY_RE.search(html):
        return False

    html = HEAD_RE.sub(lambda m: m.group(1) + PIXEL_SCRIPT, html, count=1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True


def main():
    patched, skipped = 0, 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            if not name.endswith(".html"):
                continue
            full = os.path.join(dirpath, name)
            if patch(full):
                patched += 1
            else:
                skipped += 1
    print(f"Patched: {patched}, already had pixel / skipped: {skipped}")


if __name__ == "__main__":
    main()
