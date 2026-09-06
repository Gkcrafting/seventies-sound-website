"""Run the website locally so external players receive a web referrer."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from pathlib import Path

root = Path(__file__).resolve().parents[1]
server = ThreadingHTTPServer(
    ("127.0.0.1", 8000), partial(SimpleHTTPRequestHandler, directory=str(root))
)
print("Website: http://localhost:8000/website-design/website/index.html", flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
