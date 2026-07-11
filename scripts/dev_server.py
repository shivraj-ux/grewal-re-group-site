#!/usr/bin/env python3
"""Local dev preview server -- emulates Netlify's clean-URL resolution
directly against the repo (no mirror/rsync step needed): /page serves
page.html; /page.html 301s to /page. Port comes from $PORT (set by the
harness's autoPort) with a fallback for manual runs.
"""
import os
import sys
import http.server
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT") or (sys.argv[1] if len(sys.argv) > 1 else 8910))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = self.path.split('?')[0].split('#')[0]
        if path.endswith('.html') and not path.endswith('/index.html'):
            clean = path[:-5]
            if os.path.isfile(os.path.join(ROOT, path.lstrip('/'))):
                self.send_response(301)
                self.send_header('Location', clean)
                self.end_headers()
                return
        if '.' not in os.path.basename(path) and not path.endswith('/'):
            candidate = os.path.join(ROOT, path.lstrip('/') + '.html')
            if os.path.isfile(candidate):
                self.path = path + '.html' + (('?' + self.path.split('?', 1)[1]) if '?' in self.path else '')
                return http.server.SimpleHTTPRequestHandler.do_GET(self)
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Serving {ROOT} on http://127.0.0.1:{PORT}", flush=True)
        httpd.serve_forever()
