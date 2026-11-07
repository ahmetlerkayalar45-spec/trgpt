import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# BURAYA NGROK'UN VERDİĞİ ADRESİ YAPIŞTIR (Sonunda /v1 olacak)
OLLAMA_BASE_URL = "https://giggling-stowing-relocate.ngrok-free.dev/v1"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/chat/completions",
            json={
                "model": "qwen3.5:4b", # İndirdiğin modelin adı
                "messages": [{"role": "user", "content": user_message}],
                "max_tokens": 500
            },
            timeout=120 # Model yavaş cevap verirse diye süreyi uzun tut
        )
        
        result = response.json()
        return jsonify({"reply": result['choices'][0]['message']['content']})
        
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"reply": "Aga bilgisayarımdaki model şu an cevap veremiyor, lütfen birazdan tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
