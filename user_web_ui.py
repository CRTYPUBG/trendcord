#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
User Web UI - Minimal Implementation
"""

from flask import Flask
import os

def run_user_web_ui(host='0.0.0.0', port=None, debug=False):
    """Run user web UI"""
    app = Flask(__name__)
    
    if port is None:
        port = int(os.getenv('USER_PANEL_PORT', 8080))
    
    @app.route('/')
    def home():
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Panel</title>
            <style>
                body { font-family: Arial; text-align: center; margin: 50px; }
                .success { color: green; font-size: 24px; }
            </style>
        </head>
        <body>
            <h1 class="success">✅ User Panel Active!</h1>
            <p>Port: ''' + str(port) + '''</p>
            <p>Ready for Discord OAuth</p>
            <hr>
            <p><a href="/test">Test API</a></p>
            <p><a href="/auth/callback">OAuth Callback</a></p>
        </body>
        </html>
        '''
    
    @app.route('/test')
    def test():
        return {'status': 'OK', 'port': port, 'message': 'User panel working'}
    
    @app.route('/auth/callback')
    def callback():
        return '<h1>Discord OAuth Callback Ready</h1><p><a href="/">Home</a></p>'
    
    print(f"Starting User Web UI on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
    return True

if __name__ == '__main__':
    run_user_web_ui()