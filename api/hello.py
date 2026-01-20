# Vercel Python Serverless Function - Hello World Demo
# Endpoint: /api/hello?text=your_text

from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs, urlparse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Parse query parameters
        query_params = parse_qs(urlparse(self.path).query)

        # Get 'text' parameter (default: "Hello World")
        text = query_params.get('text', ['Hello World'])[0]

        # === PYTHON MANIPULATION DEMO ===
        # This is where you can add any Python processing

        result = {
            "success": True,
            "original": text,
            "manipulations": {
                "reversed": text[::-1],
                "uppercase": text.upper(),
                "lowercase": text.lower(),
                "char_count": len(text),
                "word_count": len(text.split()),
                "with_prefix": f"[PROCESSED] {text}",
                "snake_case": text.lower().replace(" ", "_")
            },
            "message": "Python processed your input successfully!"
        }

        self.wfile.write(json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8'))
