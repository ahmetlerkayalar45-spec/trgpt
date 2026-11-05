from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import time # Bekleme için ekledik
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per day", "10 per hour"], 
    storage_uri="memory://"
)

clients = [
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.3-70b-versatile"},
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-1.5-flash"},
    {"name": "Z.ai", "client": OpenAI(api_key=os.getenv("ZAI_API_KEY"), base_url="https://api.z.ai/api/paas/v4"), "model": "glm-4-flash"},
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "open-mistral-7b"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    if len(user_message) > 300:
        return jsonify({"error": "Aga bu ne? Mesaj çok uzun, lütfen 300 karakteri geçme!"}), 400

    messages = [{"role": "system", "content": "Senin adın TRGPT. Yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    # Akıllı Fallback: Her motoru 2 kez dene, aralarda bekle
    for api in clients:
        for attempt in range(2): # Her motor için 2 deneme
            try:
                print(f"{api['name']} deneniyor (Deneme {attempt+1})...")
                response = api["client"].chat.completions.create(
                    model=api["model"],
                    messages=messages,
                    max_tokens=500
                )
                print(f"✅ {api['name']} başarılı!")
                return jsonify({"reply": response.choices[0].message.content})
            except Exception as e:
                print(f"❌ {api['name']} hatası: {e}")
                time.sleep(1) # Hata alınca 1 saniye bekle, sonra tekrar dene
                continue

    # Eğer 4 motor da 2'şer kez çökerse
    return jsonify({"error": "Tüm sunucularımız şu an çok yoğun. Lütfen 10 saniye sonra tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
