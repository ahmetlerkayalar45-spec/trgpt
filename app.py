from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Groq API Bağlantısı
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", # Groq'un güncel modeli
            messages=[
                {"role": "system", "content": "Senin adın TRGPT. Yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın. Kullanıcıya doğal bir dille cevap ver."},
                {"role": "user", "content": user_message}
            ]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        # Hata olursa ekrana yazdır ki ne olduğunu anlayalım
        print(f"HATA: {e}") 
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)