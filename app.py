from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["50 per day"])

# Tüm motorlar (Sırayla denenecek)
clients = [
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.3-70b-versatile"},
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-1.5-flash"},
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "open-mistral-7b"},
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "meta-llama/llama-3.3-70b-instruct:free"},
    {"name": "GitHub", "client": OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url="https://models.inference.ai.azure.com"), "model": "gpt-4o-mini"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Mesaj boş"}), 400

    # Sırayla motorları dene
    for api in clients:
        try:
            print(f"{api['name']} deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=[{"role": "user", "content": user_message}],
                max_tokens=500
            )
            print(f"✅ {api['name']} başarılı!")
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            print(f"❌ {api['name']} hatası: {e}")
            continue # Hata alırsa bir sonraki motora geç

    return jsonify({"error": "Tüm sunucular şu an yoğun. Lütfen birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
