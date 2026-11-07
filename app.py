from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# API koruması için hız sınırı
limiter = Limiter(get_remote_address, app=app, default_limits=["50 per day"])

# --- YAPAY ZEKA MOTORLARI (4 Farklı Sağlayıcı) ---
clients = [
    # 1. Groq (En hızlı)
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "openai/gpt-oss-120b"},
    
    # 2. Gemini (En akıllı yedek)
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-2.5-flash"},
    
    # 3. OpenRouter (Ücretsiz model)
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "openai/gpt-oss-120b:free"},
    
    # 4. Mistral (Son kale)
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "mistral-small-latest"}
]

@app.route('/')
def home():
    # Giriş derdi yok, direkt sohbet ekranını (index.html) aç
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute")
def api_chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # Hafıza ve Karakter (Yapay zekanın kimliği)
    messages = [{"role": "system", "content": "Senin adın TRGPT. Ahmet tarafından geliştirilen, yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın. Cevaplarını kısa, öz ve doğal tut."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    # Motorları sırayla dene (Fallback - Biri çökerse diğerine geçer)
    for api in clients:
        try:
            print(f"[{api['name']}] deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=messages,
                max_tokens=500
            )
            print(f"✅ [{api['name']}] BAŞARILI!")
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            print(f"❌ [{api['name']}] Hatası: {e}")
            continue

    return jsonify({"error": "Şu an tüm sunucularımız çok yoğun. Lütfen birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
