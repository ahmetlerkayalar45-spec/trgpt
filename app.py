from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# --- GÜVENLİK VE VERİTABANI AYARLARI ---
app.config['SECRET_KEY'] = 'trgpt-super-secret-key-123'
# Render için önemli: Veritabanını /tmp klasöründe tut (burası her zaman yazılabilir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/trgpt.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'

limiter = Limiter(get_remote_address, app=app, default_limits=["50 per day"])

# --- VERİTABANI MODELİ ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- YAPAY ZEKA MOTORLARI ---
clients = [
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "openai/gpt-oss-120b"},
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-2.5-flash"},
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "openai/gpt-oss-120b:free"},
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "mistral-small-latest"}
]

# --- ROTALAR ---

@app.route('/')
def index():
    # Eğer kullanıcı giriş yapmışsa doğrudan sohbet ekranını (index.html) göster
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username)
    # Giriş yapmamışsa auth (giriş/kayıt) sayfasına yönlendir
    return redirect(url_for('auth'))

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    # Zaten giriş yapmış biri buraya gelemez, ana sayfaya at
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if action == 'login':
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('index')) # Giriş başarılı, ana sayfaya (sohbete) git
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
            
        elif action == 'register':
            if len(password) < 4:
                flash('Şifreniz en az 4 karakter olmalıdır!', 'error')
            elif User.query.filter_by(username=username).first():
                flash('Bu kullanıcı adı zaten alınmış!', 'error')
            else:
                new_user = User(username=username, password_hash=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
                flash('Hesap başarıyla oluşturuldu, şimdi giriş yapabilirsiniz!', 'success')
                return redirect(url_for('auth')) # Kayıt başarılı, tekrar giriş ekranına dön

    return render_template('auth.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth'))

@app.route('/api/chat', methods=['POST'])
@login_required
@limiter.limit("5 per minute")
def api_chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # Hafıza ve Karakter
    messages = [{"role": "system", "content": "Senin adın TRGPT. Ahmet tarafından geliştirilen, yardımcı, zeki ve samimi bir Türkçe yapay zeka asistanısın. Cevaplarını kısa, öz ve doğal tut."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    # Motorları sırayla dene (Fallback)
    for api in clients:
        try:
            print(f"[{api['name']}] deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=messages,
                max_tokens=500
            )
            print(f"✅ [{api['name']}] BAŞARILI!")
            return jsonify({"reply": response.choices[0].message.content})
        except Exception as e:
            print(f"❌ [{api['name']}] Hatası: {e}")
            continue

    return jsonify({"error": "Şu an tüm sunucularımız çok yoğun. Lütfen birazdan tekrar dene."}), 500

# --- VERİTABANINI OLUŞTUR ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
