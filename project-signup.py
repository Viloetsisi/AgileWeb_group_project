#!/usr/bin/env python3
"""
Entry point for the PathFinder application.
"""
import os
from app import application

if __name__ == "__main__":
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    application.run(host=host, port=port, debug=debug)
