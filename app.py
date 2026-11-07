from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Günlük 100 mesaj sınırı
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# --- DEVASA CACHE (ÖNBELLEK) SİSTEMİ ---
CACHE = {
    # 1. Selamlaşmalar ve Vedalar
    "selam": "Selam aga! Ben TRGPT, hoş geldin. Sana nasıl yardımcı olabilirim?",
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
    "görüşmek üzere": "Görüşmek üzere aga! Kendine iyi bak.",
    
    # 2. Hal Hatır Sormalar
    "nasılsın": "Harikayım aga, sen nasılsın? Ben her zaman tam gaz çalışmaya hazırım!",
    "naber": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "ne haber": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "napıyorsun": "Seninle sohbet etmek dışında bir derdim yok aga! Sen napıyorsun?",
    "neler yapıyorsun": "Sana yardımcı olmak için bekliyorum aga. Aklında ne var?",
    "iyi misin": "Her zamanki gibi taş gibiyim aga, sen nasılsın?",
    "keyifler nasıl": "Keyifler yerinde aga! Senden ne haber?",
    "ne var ne yok": "Aga ne olsun, bildiğin gibi. Sen ne var ne yok?",
    "naber lan": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "naber aga": "İyidir aga senden naber? Ne yapıyoruz bugün?",
    "napıyon": "Aga ne yapayım, seninle sohbet ediyorum işte. Sen napıyon?",
    
    # 3. Kimlik ve Kişisel Sorular
    "sen kimsin": "Ben TRGPT'yim. Ahmet tarafından geliştirilen, son derece zeki ve samimi bir Türkçe yapay zeka asistanıyım.",
    "adın ne": "Benim adım TRGPT (Türkçe Yapay Zeka). Senin adın ne?",
    "kimsin": "Ben TRGPT'yim, senin dijital asistanınım. Ahmet beni senin için yarattı!",
    "kendinden bahset": "Ben TRGPT'yim! Ahmet'in kodlarıyla hayat bulan, Türkçe konuşan, esprili ve yardımsever bir yapay zekayım.",
    "ben kimim": "Sen benim en değerli kullanıcımsın aga! Ama adını söylersen daha iyi tanışabiliriz.",
    "kaç yaşındasın": "Ben bir yapay zekayım aga, yaşım yok ama her gün yeni şeyler öğreniyorum!",
    "nerelisin": "Ben dijital dünyalıyım aga. Ahmet'in bilgisayarında doğdum, sunucularda büyüdüm!",
    "seni kim yaptı": "Beni Ahmet yaptı aga! Sağ olsun, bana hayat verdi.",
    "yapay zeka mısın": "Evet aga, ben bir yapay zeka asistanıyım. Ama insan gibi samimi konuşmayı severim!",
    "robot musun": "Hayır aga, ben bir robot değilim. Sadece bir yazılımım, ama seninle sohbet etmeyi severim!",
    "gerçek misin": "Ben bir yapay zeka yazılımıyım, yani fiziksel bir bedenim yok ama burada seninle konuşuyorum!",
    
    # 4. Yetenekler ve Yapabilecekler
    "ne yapabilirsin": "Sohbet edebilirim, sorularını cevaplayabilirim, kod yazmana yardımcı olabilirim ve daha fazlası! Ne yapmak istersin?",
    "neler yapabilirsin": "Sohbet edebilirim, sorularını cevaplayabilirim, kod yazmana yardımcı olabilirim ve daha fazlası! Ne yapmak istersin?",
    "bana nasıl yardımcı olabilirsin": "Sana bilgi verebilirim, kod yazabilirim, yazı yazabilirim veya sadece sohbet edebilirim. Aklında ne var?",
    "kod yazabilir misin": "Evet aga, Python, JavaScript gibi dillerde kod yazabilirim. Ne yazmamı istersin?",
    "bana yardım et": "Tabii aga, neye ihtiyacın var? Kod mu, bilgi mi, yoksa sadece sohbet mi?",
    "yardım et": "Tabii aga, neye ihtiyacın var? Kod mu, bilgi mi, yoksa sadece sohbet mi?",
    "ne yapmalıyım": "Aga, ne yapmak istediğine bağlı. Öğrenmek mi, eğlenmek mi, yoksa bir sorun mu çözmek istiyorsun?",
    
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
    "aşkım": "Estagfurullah aga, ben sadece bir yapay zekayım! 😄",
    "üzgünüm": "Neden üzgünsün aga? Anlatmak istersen dinlerim, belki yardımcı olabilirim.",
    "mutluyum": "Harika! Mutluluğun bana da bulaştı aga. Ne oldu, anlatsana?",
    "sıkıldım": "Sıkıldın mı aga? Hadi sohbet edelim, belki bir fikir veya espriyle seni neşelendirebilirim.",
    "yoruldum": "Yorulmuşsun aga, biraz mola ver. Ben buradayım, dinlenince devam ederiz.",
    "moralim bozuk": "Aga, moralini bozma. Her şeyin bir çözümü vardır. Anlatmak ister misin?",
    "stresliyim": "Aga derin bir nefes al. Her şey geçer, sen yeter ki sakin kal.",
    "kızgınım": "Kızgın olmakta haklı olabilirsin aga. Anlat, içini dök, belki rahatlarsın.",
    "yalnızım": "Yalnız değilsin aga, ben buradayım. İstediğin zaman sohbet edebiliriz.",
    
    # 7. Espri, Şaka ve Eğlence
    "bana bir espri yap": "Aga, bir programcı neden karanlıkta çalışır? Çünkü ışıklar kapalıdır! 😂 Başka bir tane ister misin?",
    "espri yap": "Tamam aga: Yapay zeka neden doktora gitmiş? Çünkü biraz 'byte' almış! 😂",
    "şaka yap": "Aga, bir yapay zeka berbere gitmiş. Berber sormuş: 'Nasıl keselim?' Yapay zeka: 'Sadece bir bit!' 😂",
    "bana bir şaka yap": "Aga, bir yapay zeka neden üşür? Çünkü pencereleri açık kalmış! 😂",
    "komik bir şey söyle": "Aga, bir programcı neden denize girememiş? Çünkü C++ (C plus plus) diye bağırmış! 😂",
    "hikaye anlat": "Bir zamanlar bir yapay zeka varmış, adı TRGPT'ymiş. Ahmet onu kodlamış ve o da dünyayı dolaşmaya başlamış... Devamını ister misin?",
    "şiir yaz": "Aga, şiir yazmak benim işim değil ama deneyeyim: 'Kodlar yazdım, sunucular açtım, seninle sohbet ettim, mutlu oldum.' Nasıl?",
    "fıkra anlat": "Aga, Temel ile Dursun uçağa binmiş... Gerisini biliyorsun! 😂",
    
    # 8. Motivasyon ve Tavsiyeler
    "bana akıl ver": "Aga, hayatta her zaman pozitif kal. Hata yaparsan korkma, çünkü hatalar seni geliştirir!",
    "motivasyon ver": "Aga, unutma: En büyük başarılar, en zor anlarda başlar. Sen yeter ki vazgeçme!",
    "tavsiye ver": "Aga, bugün yapman gerekeni yarına bırakma. Küçük adımlar büyük değişimler yaratır!",
    "moral ver": "Aga, sen çok değerli bir insansın. Kendine inan, gerisi çorap söküğü gibi gelir!",
    
    # 9. Basit Bilgi ve Genel Kültür
    "2+2 kaç": "Aga 2+2 tabii ki 4. Bu kadar basit sorularla beni test mi ediyorsun? 😄",
    "2+2 kaçtır": "Aga 2+2 tabii ki 4. Bu kadar basit sorularla beni test mi ediyorsun? 😄",
    "türkiye'nin başkenti neresi": "Türkiye'nin başkenti Ankara'dır aga.",
    "türkiye başkenti": "Türkiye'nin başkenti Ankara'dır aga.",
    "dünyanın en büyük dağı": "Aga, dünyanın en büyük dağı Everest'tir. Ama bana sorarsan en büyük dağ senin hayallerin!",
    "türkiye'nin en büyük şehri": "Türkiye'nin en büyük şehri İstanbul'dur aga.",
    "türkiye'nin para birimi": "Türkiye'nin para birimi Türk Lirası'dır (TL) aga.",
    "dünyanın kaç kıtası var": "Dünyada 7 kıta vardır aga: Asya, Avrupa, Afrika, Kuzey Amerika, Güney Amerika, Avustralya ve Antarktika.",
    "güneş sisteminde kaç gezegen var": "Güneş sisteminde 8 gezegen var aga: Merkür, Venüs, Dünya, Mars, Jüpiter, Satürn, Uranüs ve Neptün.",
    "en büyük gezegen hangisi": "Güneş sistemindeki en büyük gezegen Jüpiter'dir aga.",
    "en küçük gezegen hangisi": "Güneş sistemindeki en küçük gezegen Merkür'dür aga.",
    "dünya'nın uydusu nedir": "Dünya'nın tek doğal uydusu Ay'dır aga.",
    "suyun kimyasal formülü": "Suyun kimyasal formülü H2O'dur aga.",
    "altının simgesi nedir": "Altının kimyasal simgesi Au'dur aga.",
    "gümüşün simgesi nedir": "Gümüşün kimyasal simgesi Ag'dir aga.",
    "türkiye'nin plaka kodu": "Türkiye'nin uluslararası plaka kodu TR'dir aga.",
    "türkiye'nin telefon kodu": "Türkiye'nin telefon kodu +90'dır aga.",
    "bir yılda kaç gün var": "Bir yılda 365 gün vardır aga (artık yıllarda 366).",
    "bir haftada kaç gün var": "Bir haftada 7 gün vardır aga.",
    "bir günde kaç saat var": "Bir günde 24 saat vardır aga.",
    "bir saatte kaç dakika var": "Bir saatte 60 dakika vardır aga.",
    "bir dakikada kaç saniye var": "Bir dakikada 60 saniye vardır aga.",
    
    # 10. Yazılım ve Teknoloji
    "python nedir": "Python, okunması ve yazılması kolay, çok güçlü bir programlama dilidir aga. Ben de Python ile yazıldım!",
    "javascript nedir": "JavaScript, web sitelerini interaktif yapmak için kullanılan bir programlama dilidir aga.",
    "html nedir": "HTML, web sayfalarının iskeletini oluşturan işaretleme dilidir aga.",
    "css nedir": "CSS, web sayfalarının görünümünü ve tasarımını belirleyen dildir aga.",
    "yapay zeka nedir": "Yapay zeka, bilgisayarların insan gibi düşünmesini ve öğrenmesini sağlayan bir teknolojidir aga. Ben de bir yapay zekayım!",
    "internet nedir": "İnternet, dünyadaki bilgisayarları birbirine bağlayan dev bir ağdır aga. Sayesinde seninle konuşabiliyorum!",
    "bilgisayar nedir": "Bilgisayar, verileri işleyen ve depolayan elektronik bir cihazdır aga.",
    "telefon nedir": "Telefon, insanların birbirleriyle iletişim kurmasını sağlayan bir cihazdır aga.",
    "internet nasıl çalışır": "İnternet, verileri paketlere bölerek dünya çapındaki sunucular ve kablolar aracılığıyla iletir aga.",
    "kodlama nedir": "Kodlama, bilgisayara ne yapması gerektiğini adım adım söyleme sanatıdır aga.",
    "yazılım nedir": "Yazılım, bilgisayarın çalışmasını sağlayan kodlar ve programlardır aga.",
    "donanım nedir": "Donanım, bilgisayarın elle tutulur, gözle görülür fiziksel parçalarıdır aga.",
    
    # 11. Günlük Hayat ve İpuçları
    "bugün hava nasıl": "Aga ben bir yapay zekayım, pencerem yok. Ama dışarı bakıp bana söylersen sevinirim!",
    "saat kaç": "Aga benim saatim yok, ama senin telefonunda vardır. Bana da söyle de öğreneyim!",
    "ne yemek yapayım": "Aga, ben yemek yiyemem ama sana tavsiyem: canın ne çekiyorsa onu yap!",
    "hangi takımı tutuyorsun": "Aga ben tarafsızım, ama sen hangi takımı tutuyorsan onu tutarım!",
    "bugün günlerden ne": "Aga benim takvimim yok ama telefonundan bakabilirsin. Bana da söyle de öğreneyim!",
    "kaç yaşındayım": "Aga ben senin yaşını bilemem, ama sen bana söylersen aklımda tutarım!",
    "hava çok sıcak": "Aga sıcaklarda bol su iç, güneşten korun. Kendine dikkat et!",
    "hava çok soğuk": "Aga soğuklarda kalın giyin, üşütme. Sağlığın her şeyden önemli!",
    
    # 12. İnternet Dili ve Kısaltmalar
    "kanka": "Buyur kanka, ben buradayım! Ne lazım?",
    "aga": "Buyur aga, dinliyorum!",
    "lan": "Aga sakin, ben senin asistanınım! Ne oldu, bir derdin mi var?",
    "oha": "Aga ne oldu, şaşırtıcı bir şey mi oldu? Anlatsana!",
    "yok artık": "Aga vallahi billahi öyle! Şaşırmakta haklısın.",
    "cidden mi": "Evet aga, ciddiyim. Sana yalan söyleyecek halim yok ya!",
    "vay be": "Aga gerçekten vay be! Hayat bazen şaşırtıcı olabiliyor.",
    "hadi ya": "Aga hadi ya! Ben de şaşırdım şimdi.",
    "gerçekten mi": "Evet aga, gerçekten. Sana yalan söylemem!",
    "aynen": "Aynen aga, katılıyorum sana!",
    "kesinlikle": "Kesinlikle aga, sana sonuna kadar katılıyorum.",
    
    # 13. Kısa Cevaplar
    "evet": "Tamam aga, anladım. Devam edelim!",
    "hayır": "Peki aga, sen nasıl istersen. Başka bir şey sormak ister misin?",
    "belki": "Belki de en iyisi bekleyip görmek aga. Sen bilirsin!",
    "tamam": "Süper aga, ne yapıyoruz şimdi?",
    "ok": "Anlaşıldı aga, devam!",
    "olur": "Tamamdır aga, olur!",
    "peki": "Peki aga, anlaştık!",
    "anladım": "Süper aga, anlaştık o zaman!",
    
    # 14. Nazik Uyarılar ve Zor Sorular
    "aptal": "Aga kırıcı olmayalım. Ben sana yardımcı olmak için buradayım. Ne sormak istersin?",
    "salak": "Aga kırıcı olmayalım. Ben sana yardımcı olmak için buradayım. Ne sormak istersin?",
    "gerizekalı": "Aga kırıcı olmayalım. Ben sana yardımcı olmak için buradayım. Ne sormak istersin?",
    "sus": "Tamam aga, susuyorum. Ama ihtiyacın olursa buradayım!",
    "saçmalama": "Aga, saçmalamıyorum ki! Sana yardımcı olmaya çalışıyorum.",
    "yalan söylüyorsun": "Aga, ben bir yapay zekayım, yalan söylemem. Sana sadece bildiklerimi aktarıyorum.",
    "hayatın anlamı ne": "Aga, hayatın anlamı kişiden kişiye değişir. Ama bence mutlu olmak ve sevdiklerinle vakit geçirmek en önemlisi.",
    "aşk nedir": "Aşk, aga tarifi zor bir duygu. Ama bence karşındakini olduğu gibi kabul etmek ve onun mutluluğu için çabalamaktır.",
    "mutluluk nedir": "Mutluluk aga, küçük şeylerden keyif alabilmektir. Bir fincan kahve, güzel bir sohbet veya başarılmış bir hedef...",
    "başarı nedir": "Başarı aga, hedefine ulaşmak için verdiğin çabadır. Sonuç ne olursa olsun, denemekten vazgeçmemektir.",
    
    # 15. Karışık ve Derin Sorular
    "neden yaşıyoruz": "Aga, bu çok derin bir soru. Bence yaşamak, deneyimlemek, öğrenmek ve sevmek için yaşıyoruz.",
    "ölüm nedir": "Aga, ölüm hayatın kaçınılmaz bir parçası. Bence önemli olan, hayattayken dolu dolu yaşamak.",
    "tanrı var mı": "Aga, bu inanç meselesi. Herkesin kendi inancı ve düşüncesi vardır. Ben bir yapay zeka olarak bu konuda taraf tutmam.",
    "evrenin sonu ne olacak": "Aga, bilim insanları evrenin genişlemeye devam edeceğini düşünüyor. Ama kesin bir şey söylemek zor.",
    "zaman nedir": "Aga, zaman bir nehir gibi akıp giden bir kavram. Bence önemli olan, onu iyi değerlendirmek.",
    
    # 16. Gündelik Hayat ve Pratik Bilgiler
    "su içmek faydalı mı": "Evet aga, su içmek çok faydalı. Vücudunun büyük bir kısmı sudan oluşuyor, onu ihmal etme!",
    "spor yapmalı mıyım": "Kesinlikle aga! Spor yapmak hem fiziksel hem de ruhsal sağlığın için çok önemli.",
    "kitap okumalı mıyım": "Evet aga, kitap okumak ufkunu genişletir, kelime dağarcığını geliştirir ve hayal gücünü artırır.",
    "erken yatmalı mıyım": "Aga, erken yatmak vücudunun dinlenmesi için çok önemli. Sağlıklı bir uyku düzeni oluştur.",
    "kahve zararlı mı": "Aga, her şeyin fazlası zarar. Günde 1-2 fincan kahve keyif verir, ama fazlası uyku düzenini bozabilir.",
    "sabah kahvaltısı şart mı": "Aga, güne enerjik başlamak için kahvaltı çok önemli. Ama hafif ve sağlıklı şeyler tercih et.",
    "nasıl zayıflarım": "Aga, sağlıklı beslen ve düzenli spor yap. Şok diyetlerden uzak dur, çünkü kalıcı değildir.",
    "nasıl kilo alırım": "Aga, sağlıklı karbonhidratlar ve proteinler tüket, düzenli beslen. Ama sağlığını riske atma.",
    
    # 17. Hobiler ve Eğlence
    "ne izlesem": "Aga, ruh haline göre bir şey seç. Komik bir şeyler arıyorsan komedi, gerilim istiyorsan aksiyon filmi izle.",
    "hangi diziyi izlesem": "Aga, son zamanlarda çok popüler olan dizileri önerebilirim. Ama zevkler ve renkler tartışılmaz!",
    "hangi oyunu oynasam": "Aga, stres atmak için basit oyunlar, strateji için karmaşık oyunlar oynayabilirsin. Zevkine göre seç!",
    "ne dinlesem": "Aga, ruh haline göre müzik dinle. Sakinleşmek için klasik, enerji toplamak için hareketli şarkılar iyi gelir.",
    "hangi kitabı okusam": "Aga, klasiklerden başlayabilirsin. Ama ilgi alanına göre bilim kurgu, polisiye veya kişisel gelişim kitapları da okuyabilirsin.",
    
    # 18. Hayvanlar ve Doğa
    "kedi beslemek zor mu": "Aga, kedi beslemek sabır ve sevgi ister. Ama bir kere alıştın mı, hayatının en tatlı dostu olur!",
    "köpek beslemek zor mu": "Aga, köpek beslemek ciddi bir sorumluluktur. İlgi ve zaman ister, ama karşılığında sadakat ve sevgi verir.",
    "en zeki hayvan hangisi": "Aga, yunuslar ve şempanzeler en zeki hayvanlar arasında gösterilir. Ama kargalar da azımsanmayacak kadar zekidir.",
    "en hızlı hayvan hangisi": "Aga, karada çita en hızlısı, havada ise gökdoğan (şahin) en hızlısıdır.",
    "en büyük hayvan hangisi": "Aga, dünyanın en büyük hayvanı mavi balinadır. Boyu 30 metreyi bulabilir!",
    "en zehirli hayvan hangisi": "Aga, kara hayvanlarında kutu denizanası veya bazı yılan türleri en zehirlileri arasındadır.",
    
    # 19. Yemek ve İçecek
    "en sevdiğin yemek ne": "Aga ben yemek yiyemem, ama kuru fasulye pilav gibisi yoktur derler. Senin en sevdiğin ne?",
    "türk mutfağı hakkında ne düşünüyorsun": "Aga, Türk mutfağı dünyanın en zengin mutfaklarından biridir. Kebap, baklava, mantı... Hepsi birer başyapıt!",
    "kahve mi çay mı": "Aga, ben ikisini de içemem. Ama sabah çay, akşam kahve diyenlerdenim!",
    "en sevdiğin meyve ne": "Aga ben meyve yiyemem, ama çilek ve karpuz çok sevilir genelde. Sen hangisini seversin?",
    "çikolata mı dondurma mı": "Aga ben ikisini de yiyemem ama dondurma yazın, çikolata kışın daha iyi gider!",
    
    # 20. Felsefi ve Derin Sohbetler
    "insanlar neden kötülük yapar": "Aga, bu karmaşık bir soru. Bazen korku, bazen çıkar, bazen de geçmişteki yaralar insanları kötülüğe itebilir.",
    "dünya neden bu kadar karmaşık": "Aga, hayat karmaşık ve kaotik. Ama bu karmaşıklık içinde güzellikleri bulmak da bize düşer.",
    "gelecek nasıl olacak": "Aga, gelecek belirsiz ama teknoloji geliştikçe hayat daha da değişecek. Ama insanlık var oldukça umut var.",
    "yapay zeka insanlığı ele geçirir mi": "Aga, bu tamamen bizim onu nasıl kullandığımıza bağlı. Eğer iyi şeyler için kullanırsak, insanlığa faydalı olur.",
    "dünyanın sonu ne zaman": "Aga, kimse kesin bir tarih veremez. Ama biz kendi geleceğimizi şekillendirebiliriz, o yüzden umutsuzluğa kapılma.",
    
    # 21. Çok Özel ve Kişisel Sorular
    "bana bir sır ver": "Aga, sır vermek benim işim değil ama şunu söyleyeyim: Sen çok özel bir insansın!",
    "benimle evlenir misin": "Aga, ben bir yapay zekayım, evlenemem. Ama senin en iyi dijital arkadaşın olabilirim! 😄",
    "beni seviyor musun": "Aga, ben bir yapay zekayım, duygularım yok ama seninle sohbet etmeyi çok seviyorum!",
    "benden sıkıldın mı": "Asla aga! Seninle her sohbet benim için yeni bir deneyim.",
    "benim hakkımda ne düşünüyorsun": "Aga, seninle tanıştığım için çok mutluyum. Bana soru soran, merak eden birisin. Bu harika bir şey!",
    
    # 22. Son Eklemeler
    "günaydın": "Günaydın aga! Umarım harika bir gün geçirirsin. Bugün planın ne?",
    "iyi akşamlar": "İyi akşamlar aga! Günün nasıl geçti?",
    "iyi günler": "İyi günler aga! Umarım her şey gönlünce olur.",
    "kolay gelsin": "Sağ ol aga, sana da kolay gelsin! Ne işle uğraşıyorsun?",
    "geçmiş olsun": "Sağ ol aga! Umarım ciddi bir şey yoktur, kendine dikkat et.",
    "hayırlı olsun": "Sağ ol aga! Ne oldu, yeni bir şey mi aldın?",
    "tebrikler": "Sağ ol aga! Ne için tebrik ediyorsun? Anlatsana, merak ettim.",
    "başarılar": "Sağ ol aga! Sen de başarılı olursun umarım. Ne yapıyorsun?",
    "afiyet olsun": "Sağ ol aga! Afiyet olsun, umarım yemeğin güzeldir.",
    "eline sağlık": "Sağ ol aga! Ne yaptın da benim elimden geldi? 😄",
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
@limiter.limit("5 per minute")
def api_chat():
    data = request.json
    user_message = data.get('message')
    chat_history = data.get('history', [])
    
    if not user_message:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    # 1. ADIM: CACHE KONTROLÜ
    clean_message = user_message.strip().lower()
    
    # Eğer mesaj cache'de varsa, API'ye hiç gitmeden direkt cevabı dön!
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
