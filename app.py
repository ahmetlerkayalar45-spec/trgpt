from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Hız Sınırı (DDoS ve API sömürüsünü engeller)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per day", "10 per hour"], 
    storage_uri="memory://"
)

# 4 Motorlu Sistem (Biri çökerse sırayla diğerine geçer)
clients = [
    # 1. Groq (En hızlı)
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.3-70b-versatile"},
    
    # 2. Gemini (En akıllı yedek)
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-1.5-flash"},
    
    # 3. Z.ai (Sınırsız yedek)
    {"name": "Z.ai", "client": OpenAI(api_key=os.getenv("ZAI_API_KEY"), base_url="https://api.z.ai/api/paas/v4"), "model": "glm-4-flash"},
    
    # 4. Mistral (Son kale)
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "open-mistral-7b"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute") # Dakikada en fazla 5 istek
def chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # 300 Karakter Sınırı (Kota koruması)
    if len(user_message) > 300:
        return jsonify({"error": "Aga bu ne? Mesaj çok uzun, lütfen 300 karakteri geçme!"}), 400

    # Yapay zekanın kimliği ve hafızası
    messages = [{"role": "system", "content": "Senin adın TRGPT. Yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın."}]
    messages.extend(chat_history[-10:]) # Sadece son 10 mesajı hatırla
    messages.append({"role": "user", "content": user_message})

    # Fallback Zinciri
    for api in clients:
        try:
            print(f"{api['name']} deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=messages,
                max_tokens=500 # Yapay zeka en fazla 500 token yazabilir (Kota koruması)
            )
            print(f"✅ {api['name']} başarılı!")
            return jsonify({"reply": response.choices[0].message.content})
            
        except Exception as e:
            print(f"❌ {api['name']} hatası: {e}")
            continue # Hata alırsa bir sonraki motora geç

    # Eğer 4 motor da çökerse
    return jsonify({"error": "Şu an tüm sunucularımız çok yoğun. Lütfen birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
