#!/usr/bin/env python3
"""
Zoth ASCII Magic Server (Port :8132)
Avant-Garde Image & 3D to TrueColor ASCII, Bayer Dither & SVG Server
Engineered by Neal Frazier Tech (@1nc0gn30) • NullAI Platform
"""

import argparse
import http.server
from importlib.machinery import SourceFileLoader
import json
import os
import socketserver
import sys
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(SCRIPT_DIR, "public")
CLI_PATH = os.path.join(SCRIPT_DIR, "bin", "zoth-ascii-magic")

# Dynamically import CLI module
ascii_cli = SourceFileLoader("zoth_ascii_cli", CLI_PATH).load_module()


class ZothAsciiMagicHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in ("/health", "/api/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "status": "ok",
                        "service": "zoth-ascii-magic",
                        "version": "2.7.0",
                        "port": getattr(self.server, "port", 8132),
                        "mode": "standalone-sovereign",
                        "quantizers": list(ascii_cli.RAMPS.keys()),
                        "presets": [
                            "cyberBust",
                            "liquidChrome",
                            "torus4d",
                            "merkaba",
                            "datamosh",
                            "radar",
                            "sigil",
                        ],
                    }
                ).encode("utf-8")
            )
            return

        if path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {
                        "status": "online",
                        "quantizers": list(ascii_cli.RAMPS.keys()),
                        "palettes": list(ascii_cli.PALETTES.keys()),
                        "presets": [
                            "cyberBust",
                            "liquidChrome",
                            "torus4d",
                            "merkaba",
                            "datamosh",
                            "radar",
                            "sigil",
                        ],
                        "free_open_access": True,
                    }
                ).encode("utf-8")
            )
            return

        if path == "/api/render":
            preset = query.get("preset", ["cyberBust"])[0]
            mode = query.get("mode", ["ascii"])[0]
            tube = query.get("tube", ["gold"])[0]
            cols = int(query.get("cols", [64])[0])
            no_edge = query.get("no_edge", ["0"])[0] in ("1", "true")
            no_color = query.get("no_color", ["0"])[0] in ("1", "true")
            format_type = query.get("format", ["text"])[0]

            is_html = format_type == "html"
            is_svg = format_type == "svg"

            try:
                rendered = ascii_cli.render_matrix(
                    cols=cols,
                    mode=mode,
                    preset=preset,
                    image_path=None,
                    edge=not no_edge,
                    color=not no_color,
                    html=is_html,
                    svg=is_svg,
                    tube=tube,
                )
                self.send_response(200)
                if is_svg:
                    self.send_header("Content-Type", "image/svg+xml")
                elif is_html:
                    self.send_header("Content-Type", "text/html")
                else:
                    self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                if is_svg or is_html:
                    self.wfile.write(rendered.encode("utf-8"))
                else:
                    rows = max(14, int(cols * 0.48))
                    self.wfile.write(
                        json.dumps(
                            {
                                "generator": "zoth-ascii-magic",
                                "preset": preset,
                                "mode": mode,
                                "tube": tube,
                                "cols": cols,
                                "rows": rows,
                                "output": rendered,
                            }
                        ).encode("utf-8")
                    )
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            return

        return super().do_GET()


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def main():
    parser = argparse.ArgumentParser(description="Zoth ASCII Magic Web Daemon")
    parser.add_argument("--port", type=int, default=8132, help="Port to bind (default: 8132)")
    args = parser.parse_args()

    server = ThreadingTCPServer(("127.0.0.1", args.port), ZothAsciiMagicHandler)
    server.port = args.port
    print(f"⚡ Zoth ASCII Magic server running on http://127.0.0.1:{args.port} (serving {PUBLIC_DIR})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Zoth ASCII Magic server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
