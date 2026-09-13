"""
Vercel Serverless Function Entrypoint
Exposes the FastAPI application to Vercel's ASGI runtime.
"""

import sys
import os

# Add root directory to sys.path so sibling modules (database, rule_engine, etc.) can be imported seamlessly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
