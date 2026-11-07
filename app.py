import json
import os
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# Cache dosyasını yükle
CACHE_FILE = 'cache.json'
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        CACHE = json.load(f)
else:
    CACHE = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def api_chat():
    data = request.json
    user_message = data.get('message', '').strip().lower()
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # 1. ADIM: Tam Eşleşme
    if user_message in CACHE:
        return jsonify({"reply": CACHE[user_message]})

    # 2. ADIM: Akıllı Arama (İçinde geçiyor mu?)
    for key, reply in CACHE.items():
        if key in user_message:
            return jsonify({"reply": reply})

    # 3. ADIM: Bulunamazsa
    return jsonify({"reply": "Aga bunu henüz öğrenmedim ama yakında öğreneceğim! Başka bir şey sormak ister misin?"}), 200

if __name__ == '__main__':
    app.run(debug=True)
