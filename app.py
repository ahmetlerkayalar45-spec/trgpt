from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

client = OpenAI(
    api_key=os.getenv("ZAI_API_KEY"), # Z.ai anahtarın Render'da tanımlı olmalı
    base_url="https://api.z.ai/api/paas/v4"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', []) # Frontend'den gelen geçmiş

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # Yapay zekanın kimliğini ve geçmişi ayarlıyoruz
    messages = [{"role": "system", "content": "Senin adın TRGPT. Yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın."}]
    messages.extend(chat_history) # Eski mesajları ekle
    messages.append({"role": "user", "content": user_message}) # Yeni mesajı ekle

    try:
        response = client.chat.completions.create(
            model="glm-4-flash", # Z.ai modeli
            messages=messages
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print(f"Z.ai Hatası: {e}")
        return jsonify({"error": "Sunucu yoğun veya limit doldu. Lütfen biraz sonra tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
