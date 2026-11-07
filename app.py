import os
from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Sadece Senin Modelin (Hugging Face)
HF_MODEL_ID = "ahmetaimaker/trgpt-model" 
HF_TOKEN = os.getenv("HF_TOKEN") 

# Hugging Face API Bağlantısı
hf_client = InferenceClient(model=HF_MODEL_ID, token=HF_TOKEN)

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
        print("🔄 [TRGPT Model] deneniyor...")
        response = hf_client.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        print("✅ [TRGPT Model] BAŞARILI!")
        return jsonify({"reply": response.choices[0].message.content})
        
    except Exception as e:
        print(f"⚠️ [TRGPT Model] Hatası: {e}")
        return jsonify({"reply": "Aga beynim şu an uyanıyor, lütfen 10 saniye sonra tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
