import json
import os
from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Dakikada 10 mesaj sınırı
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# Cache dosyasını yükle (Eğer dosya yoksa boş bir sözlük oluştur)
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

    # SADECE CACHE KONTROLÜ
    if user_message in CACHE:
        print(f"⚡ CACHE'DEN CEVAP VERİLDİ: {user_message}")
        return jsonify({"reply": CACHE[user_message]})
    else:
        print(f"❓ CACHE'DE YOK: {user_message}")
        return jsonify({"reply": "Aga bunu henüz öğrenmedim ama yakında öğreneceğim! Başka bir şey sormak ister misin?"}), 200

if __name__ == '__main__':
    app.run(debug=True)
