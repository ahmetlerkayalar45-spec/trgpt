import os
import time
from flask import Flask, request, jsonify, render_template
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct" 
HF_TOKEN = os.getenv("HF_TOKEN") 

client = InferenceClient(
    model=MODEL_ID,
    token=HF_TOKEN,
    base_url="https://api-inference.huggingface.co",
    timeout=60.0  # Cold start için zaman aşımını 60 saniyeye çıkar [citation:10]
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

    # Model uyanana kadar 3 kez deneme yap
    for attempt in range(3):
        try:
            print(f"🔄 Deneme {attempt + 1}: Qwen modeli çağrılıyor...")
            response = client.chat_completion(
                messages=[{"role": "user", "content": user_message}],
                max_tokens=500
            )
            print("✅ Qwen BAŞARILI!")
            return jsonify({"reply": response.choices[0].message.content})
            
        except Exception as e:
            print(f"⚠️ Deneme {attempt + 1} hatası: {str(e)[:100]}...")
            
            # Eğer hata "model yükleniyor" veya "503" ise bekle ve tekrar dene
            if "loading" in str(e).lower() or "503" in str(e) or "timeout" in str(e).lower():
                wait_time = 10 * (attempt + 1)  # 10s, 20s, 30s bekle
                print(f"⏳ Model uyanıyor, {wait_time} saniye bekleniyor...")
                time.sleep(wait_time)
                continue
            else:
                # Başka bir hata varsa (token yanlış vs.) direkt çık
                break
    
    # 3 denemeye rağmen olmadıysa
    return jsonify({"reply": "Aga beynim uyanmakta zorlanıyor, lütfen 30 saniye sonra tekrar dene!"}), 500

if __name__ == '__main__':
    app.run(debug=True)
