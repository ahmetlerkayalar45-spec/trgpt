from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, default_limits=["50 per day"])

# KENDİ BEYNİMİZ (Hugging Face)
client = OpenAI(
    api_key=os.getenv("HF_TOKEN"), 
    base_url="https://api-inference.huggingface.co/models/ahmetaimaker/trgpt-model/v1" 
)

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

    try:
        response = client.chat.completions.create(
            model="trgpt-model", 
            messages=[{"role": "user", "content": user_message}],
            max_tokens=200
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"error": "Beyin uyanmadı, birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
