from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# 1. KORUMA: Spam ve API sömürüsünü engelleyen hız sınırı
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["50 per day", "10 per hour"], 
    storage_uri="memory://"
)

# 2. ÇOKLU MOTOR (FALLBACK) SİSTEMİ - Modeller güncellendi
clients = [
    # 1. Groq (Güncel model: Llama 3.1 8B - Hızlı)
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.1-8b-instant"},
    
    # 2. Gemini (Güncel model: 2.0 Flash)
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-2.0-flash"},
    
    # 3. Mistral (Seni kurtaran motor - Stabil)
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "mistral-small-latest"},
    
    # 4. OpenRouter (Ücretsiz Llama 3.3)
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "meta-llama/llama-3.3-70b-instruct:free"},
    
    # 5. GitHub Models (Son Kale)
    {"name": "GitHub", "client": OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url="https://models.inference.ai.azure.com"), "model": "gpt-4o-mini"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute") # Dakikada en fazla 5 mesaj
def chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # 3. KORUMA: 300 Karakter Sınırı
    if len(user_message) > 300:
        return jsonify({"error": "Aga bu ne? Mesaj çok uzun, lütfen 300 karakteri geçme!"}), 400

    # 4. HAFIZA: Yapay zekanın kimliği ve son 10 mesajı hatırlaması
    messages = [{"role": "system", "content": "Senin adın TRGPT. Ahmet tarafından geliştirilen, yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    # 5. FALLBACK DÖNGÜSÜ: Sırayla motorları dene
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
            continue # Hata alırsa döngüdeki bir sonraki motora geçer

    # 6. KORUMA: Eğer 5 motor da çökerse
    return jsonify({"error": "Şu an tüm sunucularımız çok yoğun. Lütfen birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
