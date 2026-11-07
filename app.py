import os
import time
from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- MOTOR 1: SENİN EĞİTTİĞİN MODEL (Hugging Face) ---
HF_MODEL_ID = "ahmetaimaker/trgpt-model" 
HF_TOKEN = os.getenv("HF_TOKEN") 
hf_client = InferenceClient(model=HF_MODEL_ID, token=HF_TOKEN)

# --- MOTOR 2: GROQ (Hızlı Yedek) ---
groq_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

# --- MOTOR 3: GEMINI (Akıllı Yedek) ---
gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"), 
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # --- AŞAMA 1: Senin Kendi Modelin (Hugging Face) ---
    try:
        print("🔄 [TRGPT Özel Model] deneniyor...")
        response = hf_client.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        print("✅ [TRGPT Özel Model] BAŞARILI!")
        return jsonify({"reply": response.choices[0].message.content})
        
    except Exception as e:
        print(f"⚠️ [TRGPT Özel Model] Hatası (Uyanmıyor olabilir): {e}")

    # --- AŞAMA 2: Groq (Hızlı Yedek) ---
    try:
        print("🔄 [Groq Yedek] deneniyor...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        print("✅ [Groq Yedek] BAŞARILI!")
        return jsonify({"reply": response.choices[0].message.content})
        
    except Exception as e:
        print(f"⚠️ [Groq Yedek] Hatası: {e}")

    # --- AŞAMA 3: Gemini (İkinci Yedek) ---
    try:
        print("🔄 [Gemini Yedek] deneniyor...")
        response = gemini_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        print("✅ [Gemini Yedek] BAŞARILI!")
        return jsonify({"reply": response.choices[0].message.content})
        
    except Exception as e:
        print(f"⚠️ [Gemini Yedek] Hatası: {e}")

    # --- AŞAMA 4: Her Şey Çökerse ---
    return jsonify({"reply": "Aga şu an tüm sunucularımız çok yoğun. Lütfen 10 saniye sonra tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
