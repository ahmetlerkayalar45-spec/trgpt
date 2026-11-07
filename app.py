from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Günlük 200 mesaj sınırı
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day"])

# --- 7 MOTORLU YENİLMEZ YAPAY ZEKA SİSTEMİ ---
clients = [
    # 1. OpenRouter (En stabil ücretsiz model)
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "meta-llama/llama-3.1-8b-instruct:free"},
    
    # 2. Groq (En hızlı)
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.1-8b-instant"},
    
    # 3. Gemini (En akıllı)
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-1.5-flash"},
    
    # 4. Mistral
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "open-mistral-7b"},
    
    # 5. Z.ai
    {"name": "Z.ai", "client": OpenAI(api_key=os.getenv("ZAI_API_KEY"), base_url="https://api.z.ai/api/paas/v4"), "model": "glm-4-flash"},
    
    # 6. GitHub Models
    {"name": "GitHub", "client": OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url="https://models.inference.ai.azure.com"), "model": "gpt-4o-mini"},
    
    # 7. Hugging Face
    {"name": "HuggingFace", "client": OpenAI(api_key=os.getenv("HF_TOKEN"), base_url="https://api-inference.huggingface.co/v1"), "model": "meta-llama/Meta-Llama-3-8B-Instruct"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute") # Dakikada en fazla 5 (Spam koruması)
def api_chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # Karakter ve Hafıza
    messages = [{"role": "system", "content": "Senin adın TRGPT. Ahmet tarafından geliştirilen, son derece zeki, yardımcı ve samimi bir Türkçe yapay zeka asistanısın. Cevaplarını doğal, akıcı ve net ver."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    # Motorları sırayla dene (Biri çökerse diğerine geçer)
    for api in clients:
        try:
            print(f"🔄 [{api['name']}] deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=messages,
                max_tokens=800
            )
            print(f"✅ [{api['name']}] BAŞARILI!")
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            print(f"❌ [{api['name']}] Hatası: {str(e)[:100]}...")
            continue

    return jsonify({"error": "Tüm sunucular şu an yoğun. Lütfen 10 saniye sonra tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
