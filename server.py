"""
AI健康管家 - 本地开发服务器
解决浏览器CORS限制，代理请求到vivo蓝心大模型API
启动: python server.py
访问: http://localhost:8765
"""
import http.server
import urllib.request
import json
import ssl
import os

PORT = 8765
VIVO_API = 'https://api-ai.vivo.com.cn'
API_KEY = 'sk-xuanji-2026631636-d3dsS3V6dEt6bmpWQ1JzUA=='

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_POST(self):
        """Proxy POST requests to vivo API"""
        if not (self.path.startswith('/v1/') or self.path == '/api/proxy'):
            self.send_response(404)
            self.end_headers()
            return

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)

        try:
            req = urllib.request.Request(
                VIVO_API + self.path,
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + API_KEY
                },
                method='POST'
            )
            ctx = ssl.create_default_context()
            resp = urllib.request.urlopen(req, timeout=60, context=ctx)

            self.send_response(resp.getcode())
            self._cors_headers()
            for k, v in resp.getheaders():
                if k.lower() in ('content-type', 'content-length'):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self._cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        """Serve static files, with API proxy for /v1/models"""
        if self.path.startswith('/v1/'):
            try:
                req = urllib.request.Request(
                    VIVO_API + self.path,
                    headers={'Authorization': 'Bearer ' + API_KEY}
                )
                ctx = ssl.create_default_context()
                resp = urllib.request.urlopen(req, timeout=10, context=ctx)
                self.send_response(resp.getcode())
                self._cors_headers()
                self.end_headers()
                self.wfile.write(resp.read())
            except Exception as e:
                self.send_response(502)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            super().do_GET()

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"""
╔══════════════════════════════════════╗
║     🤖 AI健康管家 本地服务器         ║
║     运行中...                        ║
║     👉 http://localhost:{PORT}         ║
║     按 Ctrl+C 停止                   ║
╚══════════════════════════════════════╝
""")
    http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler).serve_forever()
