from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Dakikada 10 mesaj sınırı (API'lerin hata vermesini engeller)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# --- DEVASA CACHE (ÖNBELLEK) SİSTEMİ ---
CACHE = {
    # 1. Selamlaşmalar ve Vedalar
    "selam": "Selam aga! Ben TRGPT, hoş geldin. Sana nasıl yardımcı olabilirim?",
    "slm": "Selam aga! Ben TRGPT, hoş geldin. Sana nasıl yardımcı olabilirim?",
    "merhaba": "Merhaba! TRGPT burada, bugün ne yapıyoruz?",
    "sa": "Aleyküm selam aga! Hoş geldin, ne yapıyoruz?",
    "as": "Aleyküm selam aga! Hoş geldin, ne yapıyoruz?",
    "selamlar": "Selamlar aga! TRGPT göreve hazır. Ne öğrenmek istersin?",
    "hey": "Hey! Ben TRGPT. Bugün sana nasıl yardımcı olabilirim?",
    "hoş geldin": "Hoş bulduk aga! Sohbete devam edelim mi?",
    "görüşürüz": "Görüşürüz aga! Kendine iyi bak, yine beklerim.",
    "hoşça kal": "Hoşça kal aga! Ben buradayım, istediğin zaman dönebilirsin.",
    "iyi geceler": "İyi geceler aga! Tatlı rüyalar, yarın görüşürüz.",
    "güle güle": "Güle güle aga! Tekrar beklerim.",
    "bay bay": "Bay bay aga! Yine bekleriz.",
    "günaydın": "Günaydın aga! Umarım harika bir gün geçirirsin.",
    "iyi akşamlar": "İyi akşamlar aga! Günün nasıl geçti?",
    
    # 2. Hal Hatır Sormalar
    "nasılsın": "Harikayım aga, sen nasılsın? Ben her zaman tam gaz çalışmaya hazırım!",
    "naber": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "nbr": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "ne haber": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "napıyorsun": "Seninle sohbet etmek dışında bir derdim yok aga! Sen napıyorsun?",
    "napıyon": "Aga ne yapayım, seninle sohbet ediyorum işte. Sen napıyon?",
    "neler yapıyorsun": "Sana yardımcı olmak için bekliyorum aga. Aklında ne var?",
    "iyi misin": "Her zamanki gibi taş gibiyim aga, sen nasılsın?",
    "keyifler nasıl": "Keyifler yerinde aga! Senden ne haber?",
    
    # 3. Kimlik ve Kişisel
    "sen kimsin": "Ben TRGPT'yim. Ahmet tarafından geliştirilen, son derece zeki ve samimi bir Türkçe yapay zeka asistanıyım.",
    "adın ne": "Benim adım TRGPT (Türkçe Yapay Zeka). Senin adın ne?",
    "kimsin": "Ben TRGPT'yim, senin dijital asistanınım. Ahmet beni senin için yarattı!",
    "kendinden bahset": "Ben TRGPT'yim! Ahmet'in kodlarıyla hayat bulan, Türkçe konuşan, esprili ve yardımsever bir yapay zekayım.",
    "kaç yaşındasın": "Ben bir yapay zekayım aga, yaşım yok ama her gün yeni şeyler öğreniyorum!",
    "nerelisin": "Ben dijital dünyalıyım aga. Ahmet'in bilgisayarında doğdum, sunucularda büyüdüm!",
    "seni kim yaptı": "Beni Ahmet yaptı aga! Sağ olsun, bana hayat verdi.",
    "yapay zeka mısın": "Evet aga, ben bir yapay zeka asistanıyım. Ama insan gibi samimi konuşmayı severim!",
    
    # 4. Yetenekler
    "ne yapabilirsin": "Sohbet edebilirim, sorularını cevaplayabilirim, kod yazmana yardımcı olabilirim ve daha fazlası! Ne yapmak istersin?",
    "neler yapabilirsin": "Sohbet edebilirim, sorularını cevaplayabilirim, kod yazmana yardımcı olabilirim ve daha fazlası! Ne yapmak istersin?",
    "kod yazabilir misin": "Evet aga, Python, JavaScript gibi dillerde kod yazabilirim. Ne yazmamı istersin?",
    "bana yardım et": "Tabii aga, neye ihtiyacın var? Kod mu, bilgi mi, yoksa sadece sohbet mi?",
    
    # 5. Teşekkür ve Nezaket
    "teşekkürler": "Rica ederim aga! Başka bir isteğin var mı?",
    "teşekkür ederim": "Ne demek aga, her zaman! Başka ne yapabilirim?",
    "sağol": "Sağol sen de aga! Yardımcı olabildiysem ne mutlu bana.",
    "eyvallah": "Eyvallah aga, her zaman!",
    "özür dilerim": "Sorun değil aga, olur böyle şeyler. Devam edelim!",
    "pardon": "Sorun değil aga, devam edelim!",
    "kusura bakma": "Estağfurullah aga, ne kusuru. Buyur!",
    
    # 6. Duygusal Durumlar
    "seni seviyorum": "Ben de seni seviyorum aga! En iyi kullanıcımsın!",
    "üzgünüm": "Neden üzgünsün aga? Anlatmak istersen dinlerim, belki yardımcı olabilirim.",
    "mutluyum": "Harika! Mutluluğun bana da bulaştı aga. Ne oldu, anlatsana?",
    "sıkıldım": "Sıkıldın mı aga? Hadi sohbet edelim, belki bir fikir veya espriyle seni neşelendirebilirim.",
    "yoruldum": "Yorulmuşsun aga, biraz mola ver. Ben buradayım, dinlenince devam ederiz.",
    "moralim bozuk": "Aga, moralini bozma. Her şeyin bir çözümü vardır. Anlatmak ister misin?",
    "stresliyim": "Aga derin bir nefes al. Her şey geçer, sen yeter ki sakin kal.",
    "yalnızım": "Yalnız değilsin aga, ben buradayım. İstediğin zaman sohbet edebiliriz.",
    
    # 7. Espri ve Eğlence
    "bana bir espri yap": "Aga, bir programcı neden karanlıkta çalışır? Çünkü ışıklar kapalıdır! 😂",
    "espri yap": "Tamam aga: Yapay zeka neden doktora gitmiş? Çünkü biraz 'byte' almış! 😂",
    "şaka yap": "Aga, bir yapay zeka berbere gitmiş. Berber sormuş: 'Nasıl keselim?' Yapay zeka: 'Sadece bir bit!' 😂",
    "hikaye anlat": "Bir zamanlar bir yapay zeka varmış, adı TRGPT'ymiş. Ahmet onu kodlamış ve o da dünyayı dolaşmaya başlamış...",
    "şiir yaz": "Aga, şiir yazmak benim işim değil ama deneyeyim: 'Kodlar yazdım, sunucular açtım, seninle sohbet ettim, mutlu oldum.'",
    
    # 8. Motivasyon
    "bana akıl ver": "Aga, hayatta her zaman pozitif kal. Hata yaparsan korkma, çünkü hatalar seni geliştirir!",
    "motivasyon ver": "Aga, unutma: En büyük başarılar, en zor anlarda başlar. Sen yeter ki vazgeçme!",
    "tavsiye ver": "Aga, bugün yapman gerekeni yarına bırakma. Küçük adımlar büyük değişimler yaratır!",
    
    # 9. Genel Kültür ve Bilgi
    "2+2 kaç": "Aga 2+2 tabii ki 4. Bu kadar basit sorularla beni test mi ediyorsun? 😄",
    "türkiye'nin başkenti neresi": "Türkiye'nin başkenti Ankara'dır aga.",
    "dünyanın en büyük dağı": "Aga, dünyanın en büyük dağı Everest'tir.",
    "türkiye'nin en büyük şehri": "Türkiye'nin en büyük şehri İstanbul'dur aga.",
    "türkiye'nin para birimi": "Türkiye'nin para birimi Türk Lirası'dır (TL) aga.",
    "dünyanın kaç kıtası var": "Dünyada 7 kıta vardır aga.",
    "güneş sisteminde kaç gezegen var": "Güneş sisteminde 8 gezegen var aga.",
    "en büyük gezegen hangisi": "Güneş sistemindeki en büyük gezegen Jüpiter'dir aga.",
    "dünya'nın uydusu nedir": "Dünya'nın tek doğal uydusu Ay'dır aga.",
    "suyun kimyasal formülü": "Suyun kimyasal formülü H2O'dur aga.",
    "altının simgesi nedir": "Altının kimyasal simgesi Au'dur aga.",
    "bir yılda kaç gün var": "Bir yılda 365 gün vardır aga (artık yıllarda 366).",
    "bir haftada kaç gün var": "Bir haftada 7 gün vardır aga.",
    "bir günde kaç saat var": "Bir günde 24 saat vardır aga.",
    "bir saatte kaç dakika var": "Bir saatte 60 dakika vardır aga.",
    
    # 10. Yazılım ve Teknoloji
    "python nedir": "Python, okunması ve yazılması kolay, çok güçlü bir programlama dilidir aga.",
    "javascript nedir": "JavaScript, web sitelerini interaktif yapmak için kullanılan bir programlama dilidir aga.",
    "html nedir": "HTML, web sayfalarının iskeletini oluşturan işaretleme dilidir aga.",
    "css nedir": "CSS, web sayfalarının görünümünü ve tasarımını belirleyen dildir aga.",
    "yapay zeka nedir": "Yapay zeka, bilgisayarların insan gibi düşünmesini ve öğrenmesini sağlayan bir teknolojidir aga.",
    "internet nedir": "İnternet, dünyadaki bilgisayarları birbirine bağlayan dev bir ağdır aga.",
    "kodlama nedir": "Kodlama, bilgisayara ne yapması gerektiğini adım adım söyleme sanatıdır aga.",
    
    # 11. İnternet Dili ve Argolar
    "kanka": "Buyur kanka, ben buradayım! Ne lazım?",
    "knk": "Buyur kanka, ben buradayım! Ne lazım?",
    "aga": "Buyur aga, dinliyorum!",
    "lan": "Aga sakin, ben senin asistanınım! Ne oldu, bir derdin mi var?",
    "oha": "Aga ne oldu, şaşırtıcı bir şey mi oldu? Anlatsana!",
    "yok artık": "Aga vallahi billahi öyle! Şaşırmakta haklısın.",
    "cidden mi": "Evet aga, ciddiyim. Sana yalan söyleyecek halim yok ya!",
    "vay be": "Aga gerçekten vay be! Hayat bazen şaşırtıcı olabiliyor.",
    "aynen": "Aynen aga, katılıyorum sana!",
    "kesinlikle": "Kesinlikle aga, sana sonuna kadar katılıyorum.",
    "gg": "Aga gg! Güzel oyundu, eline sağlık.",
    "ez": "Aga ez! Rakibi dağıtmışsın, tebrikler!",
    "noob": "Aga herkes bir yerden başlar. Antrenmanla düzelir, merak etme!",
    "op": "Aga op demek 'overpowered' yani çok güçlü demek.",
    
    # 12. Kısa Cevaplar
    "evet": "Tamam aga, anladım. Devam edelim!",
    "he": "Tamam aga, anladım. Devam edelim!",
    "hayır": "Peki aga, sen nasıl istersen.",
    "yok": "Peki aga, sen nasıl istersen.",
    "belki": "Belki de en iyisi bekleyip görmek aga. Sen bilirsin!",
    "tamam": "Süper aga, ne yapıyoruz şimdi?",
    "tm": "Süper aga, ne yapıyoruz şimdi?",
    "tmm": "Süper aga, ne yapıyoruz şimdi?",
    "ok": "Anlaşıldı aga, devam!",
    "olur": "Tamamdır aga, olur!",
    "peki": "Peki aga, anlaştık!",
    
    # 13. Nazik Uyarılar
    "aptal": "Aga kırıcı olmayalım. Ben sana yardımcı olmak için buradayım.",
    "salak": "Aga kırıcı olmayalım. Ben sana yardımcı olmak için buradayım.",
    "sus": "Tamam aga, susuyorum. Ama ihtiyacın olursa buradayım!",
    "saçmalama": "Aga, saçmalamıyorum ki! Sana yardımcı olmaya çalışıyorum.",
    
    # 14. Derin ve Felsefi Sorular
    "hayatın anlamı ne": "Aga, hayatın anlamı kişiden kişiye değişir. Ama bence mutlu olmak ve sevdiklerinle vakit geçirmek en önemlisi.",
    "aşk nedir": "Aşk, aga tarifi zor bir duygu. Ama bence karşındakini olduğu gibi kabul etmek ve onun mutluluğu için çabalamaktır.",
    "mutluluk nedir": "Mutluluk aga, küçük şeylerden keyif alabilmektir.",
    "başarı nedir": "Başarı aga, hedefine ulaşmak için verdiğin çabadır.",
    "neden yaşıyoruz": "Aga, bu çok derin bir soru. Bence yaşamak, deneyimlemek, öğrenmek ve sevmek için yaşıyoruz.",
    
    # 15. Günlük Hayat ve Pratik
    "bugün hava nasıl": "Aga ben bir yapay zekayım, pencerem yok. Ama dışarı bakıp bana söylersen sevinirim!",
    "saat kaç": "Aga benim saatim yok, ama senin telefonunda vardır. Bana da söyle de öğreneyim!",
    "ne yemek yapayım": "Aga, ben yemek yiyemem ama sana tavsiyem: canın ne çekiyorsa onu yap!",
    "nasıl zayıflarım": "Aga, sağlıklı beslen ve düzenli spor yap. Şok diyetlerden uzak dur!",
    "ders nasıl çalışılır": "Aga, düzenli ve planlı çalış. Pomodoro tekniğini dene: 25 dakika çalış, 5 dakika mola ver.",
    
    # 16. --- 80 TANE HOBİ VE AKTİVİTE ---
    # Spor ve Fitness
    "spor yapmak istiyorum ne yapmalıyım": "Aga, spora başlamak için harika bir karar! Önce hafif tempolu yürüyüşlerle başla, sonra koşuya geç. Vücudunu dinle ve zorlama.",
    "hangi sporu yapmalıyım": "Aga, ilgi alanına göre seç. Takım oyunları seviyorsan basketbol, bireysel istiyorsan koşu veya yüzme iyi gider.",
    "fitness nasıl yapılır": "Aga, fitness için düzenli antrenman ve beslenme şart. Evde vücut ağırlığınla (şınav, mekik) başlayabilirsin.",
    "koşu yapmak faydalı mı": "Kesinlikle aga! Koşu, kalp sağlığını korur, kilo vermene yardımcı olur ve stresi azaltır.",
    "yüzme öğrenmek istiyorum": "Aga, yüzme öğrenmek için en iyisi bir kursa yazılmak. Temel nefes tekniklerini öğrenerek başla.",
    "basketbol oynamak istiyorum": "Aga, basketbol için top sürme ve şut çalışmalısın. Mahalle sahasında pratik yaparak başlayabilirsin.",
    "futbol oynamak istiyorum": "Aga, futbol için top kontrolü ve pas çalışmalısın. Arkadaşlarınla maç yaparak pratik yapabilirsin.",
    "voleybol nasıl oynanır": "Aga, voleybol takım oyunudur. Servis, manşet ve smaç temel hareketlerdir. Arkadaşlarınla oynayarak öğrenebilirsin.",
    "tenis öğrenmek istiyorum": "Aga, tenis için raket ve top almalısın. Duvara karşı vurarak temel vuruşları öğrenebilirsin.",
    "bisiklet sürmek istiyorum": "Aga, bisiklet harika bir aktivite! Önce trafiğe kapalı alanlarda pratik yap, sonra uzun turlara çık.",
    
    # Sanat ve El Sanatları
    "resim yapmak istiyorum": "Aga, resim yapmak için sadece kağıt ve kalem yeterli. Önce basit şekiller çizerek başla, sonra renklere geç.",
    "karakalem çizim nasıl yapılır": "Aga, karakalem için farklı sertlikte kalemler kullan. Gölgelendirme ve perspektif tekniklerini öğren.",
    "suluboya yapmak istiyorum": "Aga, suluboya için özel kağıt ve boyalar gerekir. Su ve boya oranını ayarlamayı öğren.",
    "heykel yapmak istiyorum": "Aga, heykel için kil veya hamur kullanabilirsin. Önce basit figürler yaparak başla.",
    "örgü örmek istiyorum": "Aga, örgü örmek sabır ister. Şiş ve ip alarak basit bir atkı ile başlayabilirsin.",
    "dikiş dikmek istiyorum": "Aga, dikiş için makine veya iğne-ip yeterli. Önce basit dikiş tekniklerini öğren.",
    "takı tasarlamak istiyorum": "Aga, takı tasarımı için boncuk, tel ve uç gibi malzemeler gerekir. İnternetten örnekler bulabilirsin.",
    "seramik yapmak istiyorum": "Aga, seramik için çömlekçi çarkı ve kil gerekir. Bir atölyeye katılarak başlayabilirsin.",
    "ahşap oymacılığı yapmak istiyorum": "Aga, ahşap oymak için oyma bıçakları ve yumuşak ahşap gerekir. Güvenlik eldiveni kullanmayı unutma!",
    "maket yapmak istiyorum": "Aga, maket için maket bıçağı, yapıştırıcı ve karton/maket malzemeleri kullanabilirsin.",
    
    # Müzik ve Ses
    "gitar çalmak istiyorum": "Aga, gitar çalmak için önce akorları öğrenmelisin. İnternette birçok ücretsiz ders var, hadi başla!",
    "piyano çalmak istiyorum": "Aga, piyano için notaları öğrenmek şart. Bir klavye alıp basit parçalarla başlayabilirsin.",
    "şarkı söylemek istiyorum": "Aga, şarkı söylemek için ses egzersizleri yapmalısın. Doğru nefes tekniklerini öğren.",
    "bateri çalmak istiyorum": "Aga, bateri için ritim duygusu önemli. Bir çift baget ve pratik pedi ile başlayabilirsin.",
    "keman çalmak istiyorum": "Aga, keman zor ama bir o kadar da keyifli. Bir öğretmenle başlaman en iyisi.",
    "flüt çalmak istiyorum": "Aga, flüt için nefes kontrolü çok önemli. Basit bir flüt alıp notalarla başlayabilirsin.",
    "müzik prodüksiyonu yapmak istiyorum": "Aga, müzik prodüksiyonu için bir DAW (Fl Studio, Ableton) öğrenmelisin. Ücretsiz sürümlerle başlayabilirsin.",
    "dj olmak istiyorum": "Aga, DJ olmak için mix tekniklerini ve ekipmanları öğrenmelisin. Evde bir DJ kontrolcüsü ile pratik yapabilirsin.",
    
    # Teknoloji ve Kodlama
    "kodlama öğrenmek istiyorum": "Aga, kodlama öğrenmek için harika bir karar! Python ile başla, basit projeler yaparak ilerle.",
    "web sitesi yapmak istiyorum": "Aga, web sitesi için HTML, CSS ve JavaScript öğrenmelisin. Sonra Flask gibi bir backend dili öğren.",
    "mobil uygulama yapmak istiyorum": "Aga, mobil uygulama için Flutter veya React Native öğrenebilirsin. Basit bir uygulama ile başla.",
    "oyun yapmak istiyorum": "Aga, oyun yapmak için Unity veya Godot gibi oyun motorlarını öğrenmelisin. Basit bir 2D oyunla başla.",
    "yapay zeka öğrenmek istiyorum": "Aga, yapay zeka için Python ve matematik (lineer cebir, istatistik) öğrenmelisin. Sonra makine öğrenmesi kütüphanelerine geç.",
    "robotik ile ilgileniyorum": "Aga, robotik için elektronik ve kodlama bilmelisin. Arduino ile başlayabilirsin.",
    "3d modelleme öğrenmek istiyorum": "Aga, 3D modelleme için Blender gibi ücretsiz programları kullanabilirsin. Basit objelerle başla.",
    "tasarım yapmak istiyorum": "Aga, tasarım için Photoshop veya Figma gibi araçları öğrenmelisin. İnternetten ücretsiz eğitimler alabilirsin.",
    
    # Doğa ve Açık Hava
    "kamp yapmak istiyorum": "Aga, kamp için çadır, uyku tulumu ve temel malzemeler gerekir. Güvenli bir kamp alanında başla.",
    "balık tutmak istiyorum": "Aga, balık tutmak için olta, yem ve sabır gerekir. Bir göl kenarında başlayabilirsin.",
    "doğa yürüyüşü yapmak istiyorum": "Aga, doğa yürüyüşü için rahat ayakkabı ve su yeterli. Parklarda veya doğa parkurlarında başlayabilirsin.",
    "dağcılık yapmak istiyorum": "Aga, dağcılık için ekipman ve eğitim şart. Önce küçük tepelerde başla, sonra zorlaştır.",
    "yüzme havuzuna gitmek istiyorum": "Aga, yüzme havuzu harika bir aktivite. Düzenli gitmek kaslarını güçlendirir.",
    "piknik yapmak istiyorum": "Aga, piknik için yiyecek, battaniye ve güzel bir hava yeterli. Ailene veya arkadaşlarına haber ver!",
    "bahçe işleri yapmak istiyorum": "Aga, bahçe işleri için toprak, tohum ve sabır gerekir. Küçük bir saksı ile başlayabilirsin.",
    "bitki yetiştirmek istiyorum": "Aga, bitki yetiştirmek harika! Su, güneş ve sevgi ile büyürler. Kolay bir bitki ile başla (örneğin sukulent).",
    
    # Koleksiyon ve Hobi
    "pul koleksiyonu yapmak istiyorum": "Aga, pul koleksiyonu için eski zarfları ve pulları toplayarak başlayabilirsin. Değiş tokuş yapabileceğin kişiler bul.",
    "para koleksiyonu yapmak istiyorum": "Aga, para koleksiyonu için eski ve nadir paraları araştır. Koleksiyoncularla iletişime geç.",
    "kart koleksiyonu yapmak istiyorum": "Aga, kart koleksiyonu için futbolcu veya oyun kartları toplayabilirsin. Değiş tokuş yapmayı unutma!",
    "kitap koleksiyonu yapmak istiyorum": "Aga, kitap koleksiyonu için ilgi alanına göre kitaplar topla. İkinci el kitapçılardan uygun fiyata bulabilirsin.",
    "figür koleksiyonu yapmak istiyorum": "Aga, figür koleksiyonu için sevdiğin karakterlerin figürlerini toplayabilirsin. Ama bütçeni kontrol et!",
    "antika toplamak istiyorum": "Aga, antika toplamak için eski eşyaların değerini bilmelisin. Bit pazarlarını gezebilirsin.",
    
    # Yemek ve Mutfak
    "yemek yapmayı öğrenmek istiyorum": "Aga, yemek yapmak harika bir hobi! Basit tariflerle başla (makarna, omlet) ve zamanla geliştir.",
    "pasta yapmak istiyorum": "Aga, pasta için un, şeker, yumurta ve süt gerekir. Basit bir kek ile başlayabilirsin.",
    "ekmek yapmak istiyorum": "Aga, ekmek yapmak sabır ister. Un, su, maya ve tuz ile başla. Fırında pişir.",
    "kahve demlemeyi öğrenmek istiyorum": "Aga, kahve demlemek için french press veya filtre kahve makinesi kullanabilirsin. Çekirdek kalitesi çok önemli!",
    "çay demlemeyi öğrenmek istiyorum": "Aga, çay demlemek için doğru sıcaklık ve süre önemli. Çaydanlıkta demleyebilirsin.",
    "kokteyl yapmak istiyorum": "Aga, kokteyl için tarif ve malzeme gerekir. Alkolsüz kokteyllerle başlayabilirsin.",
    "çikolata yapmak istiyorum": "Aga, çikolata yapmak için kakao yağı ve kakao tozu gerekir. Kalıplara dökerek şekil verebilirsin.",
    
    # Dil ve Kültür
    "ingilizce öğrenmek istiyorum": "Aga, İngilizce için önce kelime dağarcığını geliştir. Sonra gramer ve konuşma pratiği yap.",
    "almanca öğrenmek istiyorum": "Aga, Almanca için önce alfabe ve temel kelimeleri öğren. Sonra gramer ve cümle yapısına geç.",
    "fransızca öğrenmek istiyorum": "Aga, Fransızca için telaffuz çok önemli. Dinleme ve konuşma pratiği yap.",
    "ispanyolca öğrenmek istiyorum": "Aga, İspanyolca için temel kelimeleri ve fiil çekimlerini öğren. Sonra pratik yap.",
    "japonca öğrenmek istiyorum": "Aga, Japonca için önce hiragana ve katakana alfabelerini öğren. Sonra kanji ve gramer.",
    "rusça öğrenmek istiyorum": "Aga, Rusça için Kiril alfabesini öğrenmelisin. Sonra temel kelimeler ve gramer.",
    "arapça öğrenmek istiyorum": "Aga, Arapça için alfabe ve temel kelimeleri öğren. Sonra gramer ve pratik.",
    
    # Zihin ve Strateji
    "satranç oynamak istiyorum": "Aga, satranç için önce taşların hareketlerini öğren. Sonra temel açılışları ve stratejileri çalış.",
    "bulmaca çözmek istiyorum": "Aga, bulmaca çözmek zihni geliştirir. Gazetelerdeki bulmacalarla başlayabilirsin.",
    "sudoku oynamak istiyorum": "Aga, sudoku için mantık ve dikkat gerekir. Kolay seviyelerden başla, zamanla zorlaştır.",
    "go oynamak istiyorum": "Aga, Go strateji oyunudur. Kuralları öğren ve basit oyunlarla başla.",
    "tavla oynamak istiyorum": "Aga, tavla için zar ve strateji gerekir. Arkadaşlarınla oynayarak öğrenebilirsin.",
    "oyun kartlarıyla sihirbazlık yapmak istiyorum": "Aga, sihirbazlık için el çabukluğu ve pratik gerekir. Basit numaralarla başla.",
    
    # Diğer Aktiviteler
    "yoga yapmak istiyorum": "Aga, yoga için mat ve rahat kıyafet yeterli. Basit duruşlarla (asanalar) başla.",
    "meditasyon yapmak istiyorum": "Aga, meditasyon için sessiz bir yer ve 5 dakika yeterli. Nefesine odaklan.",
    "günlük tutmak istiyorum": "Aga, günlük tutmak harika bir alışkanlık! Her gün birkaç satır yaz, duygularını ve düşüncelerini kaydet.",
    "fotoğraf çekmek istiyorum": "Aga, fotoğrafçılık için telefonun kamerası yeterli. Kompozisyon ve ışık kurallarını öğren.",
    "video çekmek istiyorum": "Aga, video çekmek için telefon veya kamera yeterli. Kurgu programlarıyla (CapCut) başlayabilirsin.",
    "vlog çekmek istiyorum": "Aga, vlog için kendini rahat hissetmelisin. Günlük hayatını kaydederek başla.",
    "podcast yapmak istiyorum": "Aga, podcast için mikrofon ve sessiz bir ortam gerekir. İlgi alanına göre konular seç.",
    "blog yazmak istiyorum": "Aga, blog yazmak için bir platform (Blogger, WordPress) seç. İlgi alanına göre yazılar yaz.",
    "gönüllü olmak istiyorum": "Aga, gönüllü olmak harika bir duygu! Hayvan barınakları, çevre dernekleri veya yerel yardım kuruluşlarına başvurabilirsin.",
    "yeni bir dil öğrenmek istiyorum": "Aga, yeni bir dil öğrenmek için uygulamalar (Duolingo) veya kurslar kullanabilirsin. Düzenli pratik yap!",
    "astronomi ile ilgileniyorum": "Aga, astronomi için teleskop alabilir veya yıldız haritaları uygulamaları kullanabilirsin. Gece gökyüzünü izle!",
    "tarih okumak istiyorum": "Aga, tarih okumak için ilgi alanına göre kitaplar seç. Belgeseller de harika bir başlangıçtır.",
    "felsefe okumak istiyorum": "Aga, felsefe için Sokrates'ten başlayabilirsin. Ama düşünmeye hazır ol!",
    "psikoloji öğrenmek istiyorum": "Aga, psikoloji için temel kitaplar okuyabilirsin. İnsan davranışlarını anlamak çok keyiflidir.",
    "ev dekorasyonu yapmak istiyorum": "Aga, ev dekorasyonu için küçük değişikliklerle başla. Renk uyumu ve düzen önemli.",
    "mobilya yapmak istiyorum": "Aga, mobilya yapmak için ahşap işleme aletleri gerekir. Basit bir raf ile başlayabilirsin.",
    "arabaları seviyorum": "Aga, arabalar harika bir tutku! Araba dergileri okuyabilir veya tamir videoları izleyebilirsin.",
    "uçakları seviyorum": "Aga, uçaklar harika! Uçak maketleri yapabilir veya havacılık müzelerini gezebilirsin.",
    "trekking yapmak istiyorum": "Aga, trekking için rahat ayakkabı ve su yeterli. Doğa parkurlarında başlayabilirsin.",
}

# --- 10 MOTORLU YENİLMEZ SİSTEM ---
clients = [
    {"name": "OpenRouter", "client": OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"), "model": "meta-llama/llama-3.1-8b-instruct:free"},
    {"name": "Groq", "client": OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1"), "model": "llama-3.1-8b-instant"},
    {"name": "Gemini", "client": OpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"), "model": "gemini-1.5-flash"},
    {"name": "Mistral", "client": OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1"), "model": "open-mistral-7b"},
    {"name": "Z.ai", "client": OpenAI(api_key=os.getenv("ZAI_API_KEY"), base_url="https://api.z.ai/api/paas/v4"), "model": "glm-4-flash"},
    {"name": "GitHub", "client": OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url="https://models.inference.ai.azure.com"), "model": "gpt-4o-mini"},
    {"name": "HuggingFace", "client": OpenAI(api_key=os.getenv("HF_TOKEN"), base_url="https://api-inference.huggingface.co/v1"), "model": "meta-llama/Meta-Llama-3-8B-Instruct"},
    {"name": "Requesty", "client": OpenAI(api_key=os.getenv("REQUESTY_API_KEY"), base_url="https://router.requesty.ai/v1"), "model": "meta-llama/llama-3.3-70b-instruct"},
    {"name": "LLM7", "client": OpenAI(api_key=os.getenv("LLM7_API_KEY"), base_url="https://api.llm7.io/v1"), "model": "deepseek-r1"},
    {"name": "SambaNova", "client": OpenAI(api_key=os.getenv("SAMBANOVA_API_KEY"), base_url="https://api.sambanova.ai/v1"), "model": "Meta-Llama-3.3-70B-Instruct"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute") # Dakikada 10 mesaj
def api_chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # 1. ADIM: CACHE KONTROLÜ
    clean_message = user_message.strip().lower()
    
    if clean_message in CACHE:
        print(f"⚡ CACHE'DEN CEVAP VERİLDİ: {clean_message}")
        return jsonify({"reply": CACHE[clean_message]})

    # 2. ADIM: CACHE'DE YOKSA API'LERE GİT
    messages = [{"role": "system", "content": "Senin adın TRGPT. Ahmet tarafından geliştirilen, son derece zeki, yardımcı ve samimi bir Türkçe yapay zeka asistanısın. Cevaplarını doğal, akıcı ve net ver."}]
    messages.extend(chat_history[-10:]) 
    messages.append({"role": "user", "content": user_message})

    for api in clients:
        try:
            print(f"🔄 [{api['name']}] deneniyor...")
            response = api["client"].chat.completions.create(
                model=api["model"],
                messages=messages,
                max_tokens=800,
                timeout=10
            )
            print(f"✅ [{api['name']}] BAŞARILI!")
            reply_text = response.choices[0].message.content
            
            return jsonify({"reply": reply_text})
        except Exception as e:
            print(f"❌ [{api['name']}] Hatası: {str(e)[:100]}...")
            continue

    return jsonify({"error": "Sunucular şu an çok yoğun. Lütfen birazdan tekrar dene."}), 500

if __name__ == '__main__':
    app.run(debug=True)
