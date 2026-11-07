import os
from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# GATED OLMAYAN, TAMAMEN ÜCRETSİZ VE ÇOK ZEKİ MODEL (Qwen)
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct" 
HF_TOKEN = os.getenv("HF_TOKEN") 

client = InferenceClient(
    model=MODEL_ID,
    token=HF_TOKEN,
    base_url="https://api-inference.huggingface.co" 
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

    try:
        print("🔄 Qwen modeli deneniyor...")
        response = client.chat_completion(
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        print("✅ Qwen BAŞARILI!")
        return jsonify({"reply": response.choices[0].message.content})
        
    except Exception as e:
        print(f"⚠️ Qwen Hatası: {e}")
        return jsonify({"reply": "Aga beynim şu an uyanıyor, lütfen 10 saniye sonra tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
