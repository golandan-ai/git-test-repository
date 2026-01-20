# Vercel Python Serverless Function - SQL Query Executor
# Endpoint: /api/query?sql=SELECT...
# Purpose: Execute validated SELECT queries against Supabase

from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Configuration
        SUPABASE_URL = 'https://skbmyruppgthmfytofvf.supabase.co'
        SUPABASE_KEY = 'sb_publishable_J8MCBOmLuznjVBatY4TRTw_pXF_1Oyv'

        # Parse query parameters
        query_string = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query_string)

        # Get SQL parameter
        sql = params.get('sql', [''])[0]

        if not sql:
            # No SQL provided - return help
            response = {
                "success": False,
                "error": "No SQL query provided",
                "usage": "/api/query?sql=SELECT * FROM test01",
                "hint": "First fetch /api/schema to see database structure"
            }
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            return

        # === SECURITY VALIDATION ===
        sql_upper = sql.upper().strip()

        # 1. Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            response = {
                "success": False,
                "error": "Only SELECT queries allowed",
                "rejected_query": sql
            }
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            return

        # 2. Block dangerous keywords
        blocked_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE',
                          'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', '--', ';']

        for keyword in blocked_keywords:
            if keyword in sql_upper:
                response = {
                    "success": False,
                    "error": f"Blocked keyword detected: {keyword}",
                    "rejected_query": sql
                }
                self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
                return

        # 3. Only allow specific tables
        allowed_tables = ['test01']

        # Simple check - must mention an allowed table
        has_allowed_table = any(table in sql_upper for table in [t.upper() for t in allowed_tables])
        if not has_allowed_table:
            response = {
                "success": False,
                "error": f"Query must use allowed tables: {allowed_tables}",
                "rejected_query": sql
            }
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
            return

        # === EXECUTE QUERY VIA SUPABASE RPC ===
        try:
            # Use Supabase's PostgREST endpoint with raw SQL via RPC
            # Note: This requires a database function or we use the REST API differently

            # For simplicity, parse the SQL and convert to PostgREST format
            # This is a basic implementation - handles common SELECT patterns

            # Extract table name (basic parsing)
            table_match = re.search(r'FROM\s+(\w+)', sql_upper)
            if not table_match:
                raise Exception("Could not parse table name from query")

            table_name = table_match.group(1).lower()

            # Build PostgREST URL
            rest_url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*"

            # Parse WHERE clause if exists
            where_match = re.search(r'WHERE\s+(.+?)(?:ORDER|LIMIT|$)', sql_upper, re.IGNORECASE)
            if where_match:
                where_clause = where_match.group(1).strip()

                # Handle ILIKE pattern: column ILIKE '%value%'
                ilike_match = re.search(r"(\w+)\s+ILIKE\s+'%(.+?)%'", sql, re.IGNORECASE)
                if ilike_match:
                    column = ilike_match.group(1)
                    value = ilike_match.group(2)
                    rest_url += f"&{column}=ilike.*{urllib.parse.quote(value)}*"

                # Handle simple equality: column = value
                eq_match = re.search(r"(\w+)\s*=\s*(\d+)", where_clause)
                if eq_match:
                    column = eq_match.group(1).lower()
                    value = eq_match.group(2)
                    rest_url += f"&{column}=eq.{value}"

                # Handle less than or equal: column <= value
                lte_match = re.search(r"(\w+)\s*<=\s*(\d+)", where_clause)
                if lte_match:
                    column = lte_match.group(1).lower()
                    value = lte_match.group(2)
                    rest_url += f"&{column}=lte.{value}"

                # Handle greater than or equal: column >= value
                gte_match = re.search(r"(\w+)\s*>=\s*(\d+)", where_clause)
                if gte_match:
                    column = gte_match.group(1).lower()
                    value = gte_match.group(2)
                    rest_url += f"&{column}=gte.{value}"

            # Parse LIMIT if exists
            limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
            if limit_match:
                rest_url += f"&limit={limit_match.group(1)}"

            # Make request to Supabase
            req = urllib.request.Request(rest_url)
            req.add_header('apikey', SUPABASE_KEY)
            req.add_header('Authorization', f'Bearer {SUPABASE_KEY}')

            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            # Format response
            response = {
                "success": True,
                "query": sql,
                "record_count": len(data),
                "results": data
            }

        except Exception as e:
            response = {
                "success": False,
                "error": str(e),
                "query": sql,
                "hint": "Complex queries may not be fully supported. Try simpler SELECT statements."
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
