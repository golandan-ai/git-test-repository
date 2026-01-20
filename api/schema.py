# Vercel Python Serverless Function - Database Schema
# Endpoint: /api/schema
# Purpose: Chatbots fetch this to learn the database structure

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        schema = {
            "database": "Liaoshi Research Database",
            "description": "Historical records from the History of Liao (遼史)",
            "api_endpoints": {
                "schema": "/api/schema - You are here. Database structure.",
                "query": "/api/query?sql=YOUR_SELECT_QUERY - Execute SQL (SELECT only)",
                "search": "/api/search?q=keyword - Simple keyword search",
                "search_all": "/api/search?all=true - Get all records"
            },
            "tables": {
                "test01": {
                    "description": "Main table with historical records",
                    "row_count": "3 (test data)",
                    "columns": {
                        "id": {
                            "type": "integer",
                            "description": "Primary key, auto-increment"
                        },
                        "created_at": {
                            "type": "timestamp",
                            "description": "Record creation time"
                        },
                        "chinese_verse": {
                            "type": "text",
                            "description": "Original Chinese text from Liaoshi"
                        },
                        "translated": {
                            "type": "text",
                            "description": "English translation"
                        },
                        "chapter_n": {
                            "type": "integer",
                            "description": "Chapter number (1-116 in full Liaoshi)"
                        },
                        "key_words": {
                            "type": "text",
                            "description": "Comma-separated keywords for searching"
                        }
                    }
                }
            },
            "sample_sql_queries": [
                {
                    "description": "Get all records",
                    "sql": "SELECT * FROM test01"
                },
                {
                    "description": "Search by keyword",
                    "sql": "SELECT * FROM test01 WHERE key_words ILIKE '%horses%'"
                },
                {
                    "description": "Filter by chapter",
                    "sql": "SELECT * FROM test01 WHERE chapter_n <= 5"
                },
                {
                    "description": "Select specific columns",
                    "sql": "SELECT chinese_verse, translated FROM test01"
                },
                {
                    "description": "Combined filter",
                    "sql": "SELECT * FROM test01 WHERE key_words ILIKE '%emperor%' AND chapter_n = 1"
                },
                {
                    "description": "Count records",
                    "sql": "SELECT COUNT(*) FROM test01"
                }
            ],
            "instructions_for_chatbots": {
                "step1": "Read this schema to understand the database structure",
                "step2": "Generate a SELECT query based on user's question",
                "step3": "Call /api/query?sql=YOUR_QUERY (URL-encode the SQL)",
                "step4": "Format the JSON response according to user's preferred format",
                "security": "Only SELECT queries are allowed. No INSERT, UPDATE, DELETE, DROP."
            },
            "current_data_sample": [
                "Record 1: 契丹遣使獻馬五百匹於宋 - The Khitan sent envoys to present 500 horses to Song (Chapter 5, keywords: horses, tribute, Song, Khitan)",
                "Record 2: 遼太祖阿保機建國 - Liao Taizu Abaoji established the state (Chapter 1, keywords: Abaoji, founding, emperor)",
                "Record 3: 上京臨潢府為遼都城 - Shangjing Linhuang Prefecture was the Liao capital (Chapter 2, keywords: Shangjing, capital, city)"
            ]
        }

        self.wfile.write(json.dumps(schema, ensure_ascii=False, indent=2).encode('utf-8'))
