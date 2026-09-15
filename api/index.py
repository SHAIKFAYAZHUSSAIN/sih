"""
Vercel Serverless Function Entrypoint
Exposes the FastAPI application to Vercel's ASGI runtime.
"""

import sys
import os

import traceback

# Add root directory to sys.path so sibling modules (database, rule_engine, etc.) can be imported seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import app
except Exception as e:
    err_tb = traceback.format_exc()
    print("FATAL ERROR ON VERCEL STARTUP:\n" + err_tb, file=sys.stderr)
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    
    app = FastAPI(title="LMPC SmartInspector Startup Diagnostic")
    
    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def diagnostic_fallback(full_path: str):
        return HTMLResponse(
            f"""<!DOCTYPE html>
            <html>
            <head>
                <title>Serverless Startup Error</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, monospace; padding: 30px; background: #0f172a; color: #f1f5f9; }}
                    .card {{ max-width: 900px; margin: 0 auto; background: #1e293b; border: 1px solid #ef4444; border-radius: 12px; padding: 24px; }}
                    h1 {{ color: #f87171; font-size: 20px; margin-top: 0; }}
                    pre {{ background: #090d16; padding: 16px; border-radius: 8px; color: #fca5a5; overflow-x: auto; font-size: 13px; line-height: 1.5; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Serverless Function Startup Exception</h1>
                    <p>An uncaught Python exception occurred while initializing <code>api/index.py</code>:</p>
                    <pre>{err_tb}</pre>
                </div>
            </body>
            </html>""",
            status_code=500
        )
