from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Hugging Face'deki senin modelinin adı
MODEL_ID = "ahmetaimaker/trgpt-model" 
HF_TOKEN = os.getenv("HF_TOKEN") 

# Hugging Face API İstemcisi
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    try:
        # Hugging Face API'sine istek at
        response = client.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"reply": "Beynim şu an uyanıyor, lütfen 10 saniye sonra tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
