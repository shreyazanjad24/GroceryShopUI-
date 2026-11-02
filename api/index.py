import os
import sys

# Ensure root directory is in Python path for Vercel serverless execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

