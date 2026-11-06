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
    default_limits=["50 per day", "10 per hour"], 
    storage_uri="memory://"
)

# Sadece Groq motoru (Çalıştığını biliyoruz)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

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

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print(f"Groq Hatası: {e}")
        return jsonify({"error": "Sunucu yoğun. Lütfen 10 saniye sonra tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
