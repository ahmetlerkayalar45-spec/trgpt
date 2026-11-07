import os
import torch
from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Hugging Face token'ın (Render'da Environment'a ekle)
HF_TOKEN = os.getenv("HF_TOKEN") 

# Model isimleri
BASE_MODEL = "unsloth/llama-3-8b-Instruct-bnb-4bit"
ADAPTER_MODEL = "ahmetaimaker/trgpt-model"

print("Modeller yükleniyor, lütfen bekleyin...")

# 1. Tokenizer'ı yükle
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, token=HF_TOKEN)

# 2. Ana modeli yükle (4-bit olarak, RAM tasarrufu için)
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    token=HF_TOKEN,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)

# 3. Senin eğittiğin TRGPT karakterini (Adaptörü) yükle
model = PeftModel.from_pretrained(model, ADAPTER_MODEL, token=HF_TOKEN)

# 4. Modeli birleştir (Merge) - Artık tek parça halinde
model = model.merge_and_unload()

# 5. Metin üretim hattını (Pipeline) oluştur
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

print("✅ TRGPT beyni hazır!")

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
        # Modelden cevap üret
        prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        result = generator(
            prompt, 
            max_new_tokens=200, 
            do_sample=True, 
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )
        
        # Sadece asistanın cevabını al
        full_text = result[0]['generated_text']
        reply = full_text.split("<|start_header_id|>assistant<|end_header_id|>\n\n")[-1]
        
        return jsonify({"reply": reply.strip()})
        
    except Exception as e:
        print(f"Hata: {e}")
        return jsonify({"reply": "Aga beynim çok yoruldu, birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
