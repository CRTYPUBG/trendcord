from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>User Panel Working!</h1><p>Port 8080 Active</p>'

@app.route('/auth/callback')
def callback():
    return '<h1>OAuth Ready</h1>'

if __name__ == '__main__':
    print("Starting minimal panel on port 8080...")
    app.run(host='0.0.0.0', port=8080)