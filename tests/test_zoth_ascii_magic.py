import json
import os
import sys
import threading
import urllib.request
from importlib.machinery import SourceFileLoader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
from server import ZothAsciiMagicHandler, ThreadingTCPServer, ascii_cli


def test_sdf_and_quantizers_braille_bayer_svg():
    assert "braille" in ascii_cli.RAMPS
    assert "bayer8" in ascii_cli.RAMPS
    out_braille = ascii_cli.render_matrix(
        cols=32,
        mode="braille",
        preset="liquidChrome",
        image_path=None,
        edge=True,
        color=False,
        html=False,
        svg=False,
        tube="cyan",
    )
    lines = out_braille.splitlines()
    assert len(lines) >= 14
    assert len(lines[0]) == 32

    out_svg = ascii_cli.render_matrix(
        cols=24,
        mode="bayer8",
        preset="merkaba",
        image_path=None,
        edge=True,
        color=False,
        html=False,
        svg=True,
        tube="gold",
    )
    assert "<svg " in out_svg and "</svg>" in out_svg


def test_http_endpoints_health_status_and_render():
    httpd = ThreadingTCPServer(("127.0.0.1", 0), ZothAsciiMagicHandler)
    port = httpd.server_address[1]
    httpd.port = port
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health") as r:
            health = json.loads(r.read().decode())
            assert health["status"] == "ok"
            assert health["service"] == "zoth-ascii-magic"

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/render?preset=torus4d&mode=braille&cols=28&no_color=1") as r:
            rendered = json.loads(r.read().decode())
            assert rendered["generator"] == "zoth-ascii-magic"
            assert rendered["preset"] == "torus4d"
            assert rendered["cols"] == 28
            assert len(rendered["output"].splitlines()) >= 13
    finally:
        httpd.shutdown()
        httpd.server_close()
