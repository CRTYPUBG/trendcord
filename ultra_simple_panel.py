#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ultra Basit Kullanici Paneli
Port 8080'de calisir
"""

from flask import Flask

app = Flask(__name__)

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
            .info { color: blue; }
        </style>
    </head>
    <body>
        <h1 class="success">✅ User Panel Active!</h1>
        <p class="info">Port 8080 is working</p>
        <p>Ready for ngrok tunnel</p>
        <hr>
        <p><a href="/test">Test API</a></p>
        <p><a href="/auth/callback">OAuth Test</a></p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {'status': 'OK', 'port': 8080, 'message': 'Working'}

@app.route('/auth/callback')
def callback():
    return '<h1>OAuth Callback Ready</h1><p><a href="/">Home</a></p>'

if __name__ == '__main__':
    print("=" * 40)
    print("Ultra Simple User Panel")
    print("Port: 8080")
    print("URL: http://localhost:8080")
    print("=" * 40)
    app.run(host='0.0.0.0', port=8080, debug=False)