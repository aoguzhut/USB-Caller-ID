import sqlite3
import ctypes
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import threading
import logging
import pystray
from PIL import Image, ImageDraw

# Flask loglarını sustur
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DB_NAME = os.path.join(BASE_DIR, 'gorusmeler.db')
DLL_PATH = os.path.join(BASE_DIR, 'cid.dll')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.secret_key = 'cok_gizli_ve_guvenli_bir_anahtar'
ADMIN_USER = 'admin'
ADMIN_PASS = '123456'
aktif_hatlar = {} 
console_visible = False 

def log_yaz(mesaj):
    if console_visible:
        try:
            print(mesaj)
            sys.stdout.flush()
        except: pass

# GELİŞMİŞ TELEFON PARSER MOTORU
def temizle_ve_formatla(n, sadece_temiz=False):
    if not n: return ""
    n = "".join([c for c in n if c.isdigit()])
    
    # 1. Senaryo: Ülke koduyla gelmiş (Örn: 90 505 462 60 23 -> 12 hane)
    if n.startswith("90") and len(n) == 12:
        n = "0" + n[2:]
    # 2. Senaryo: Santral dış hat çıkışı olarak '9' eklemiş (Örn: 9 0505 462 60 23 -> 12 hane)
    elif n.startswith("90") and len(n) == 11:
        n = n[1:] # Sadece baştaki 9'u siler, 0 kalır
    # 3. Senaryo: Saf 10 hane gelmiş (Örn: 505 462 60 23), başına 0 ekle
    elif len(n) == 10 and not n.startswith("0"):
        n = "0" + n
        
    if sadece_temiz:
        return n
        
    # Sadece nizami 11 haneli numaraları (0555...) boşluklu formata sok
    if len(n) == 11 and n.startswith("0"): 
        return f"0 {n[1:4]} {n[4:7]} {n[7:9]} {n[9:11]}"
    
    return n # Hiçbir formata uymuyorsa olduğu gibi bırak

app.jinja_env.filters['format_phone'] = lambda n: temizle_ve_formatla(n)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS gorusmeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sira_no INTEGER, telefon_no TEXT,
            baslangic_zamani TEXT, bitis_zamani TEXT, toplam_sure INTEGER, durum TEXT)''')
    try: cursor.execute("ALTER TABLE gorusmeler ADD COLUMN notlar TEXT DEFAULT ''")
    except: pass 
    conn.commit()
    conn.close()

def get_today_call_count():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM gorusmeler WHERE baslangic_zamani LIKE ?", (today + '%',))
    count = cursor.fetchone()[0]
    conn.close()
    return count + 1

CallerIDFuncType = ctypes.CFUNCTYPE(None, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p)
SignalFuncType = ctypes.CFUNCTYPE(None, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)

@CallerIDFuncType
def CallerIDEvent(DeviceSerial, Line, PhoneNumber, DateTime, Other):
    if not PhoneNumber: return
    temiz_numara = "".join([c for c in PhoneNumber if c.isdigit()])
    hat_no = str(int(Line))
    
    if len(temiz_numara) >= 7:
        su_an = datetime.now()
        su_an_str = su_an.strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()
        sira_no = get_today_call_count()
        cursor.execute('''INSERT INTO gorusmeler (sira_no, telefon_no, baslangic_zamani, durum, notlar)
            VALUES (?, ?, ?, ?, '')''', (sira_no, temiz_numara, su_an_str, 'Çalıyor/Aktif'))
        db_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        aktif_hatlar[hat_no] = {"id": db_id, "baslangic": su_an}
        log_yaz(f"[{su_an.strftime('%H:%M:%S')}] ==> YENİ ÇAĞRI: {temiz_numara} (Hat: {hat_no})")

@SignalFuncType
def SignalEvent(DeviceModel, DeviceSerial, Signal1, Signal2, Signal3, Signal4):
    sinyaller = {"1": Signal1, "2": Signal2, "3": Signal3, "4": Signal4}
    for hat_no, sinyal_durumu in sinyaller.items():
        if hat_no in aktif_hatlar and sinyal_durumu in [0, 40]:
            cagri_bilgisi = aktif_hatlar.pop(hat_no)
            su_an = datetime.now()
            su_an_str = su_an.strftime('%Y-%m-%d %H:%M:%S')
            gecen_sure = int((su_an - cagri_bilgisi["baslangic"]).total_seconds())
            durum = "Cevaplandı" if gecen_sure >= 5 else "Cevapsız"
            
            conn = sqlite3.connect(DB_NAME, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''UPDATE gorusmeler SET bitis_zamani = ?, toplam_sure = ?, durum = ?
                WHERE id = ?''', (su_an_str, gecen_sure, durum, cagri_bilgisi["id"]))
            conn.commit()
            conn.close()
            log_yaz(f"[{su_an.strftime('%H:%M:%S')}] ==> ÇAĞRI BİTTİ. Süre: {gecen_sure} Sn ({durum})")

def baslat_donanim():
    init_db()
    if not os.path.exists(DLL_PATH): return
    try:
        cid_dll = ctypes.CDLL(DLL_PATH)
        SetEvents = getattr(cid_dll, "SetEvents")
        SetEvents.argtypes = [CallerIDFuncType, SignalFuncType]
        SetEvents.restype = None
        SetEvents(CallerIDEvent, SignalEvent)
    except Exception as e: pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error="Hatalı giriş!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/gorusmeler')
def api_gorusmeler():
    if not session.get('logged_in'): return jsonify({"data": []}), 401
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, sira_no, telefon_no, baslangic_zamani, bitis_zamani, toplam_sure, durum, notlar FROM gorusmeler ORDER BY id ASC")
    veriler = cursor.fetchall()
    conn.close()
    
    sonuc = []
    gunluk_sayac = {}
    
    for s in veriler:
        ham_no = s[2] if s[2] else ""
        temiz_no = temizle_ve_formatla(ham_no, sadece_temiz=True)
        
        b_zamani = s[3] if s[3] else ""
        tarih = b_zamani[:10]
        
        # Günlük Sayaç Algoritması
        if tarih not in gunluk_sayac: gunluk_sayac[tarih] = {}
        if temiz_no not in gunluk_sayac[tarih]: gunluk_sayac[tarih][temiz_no] = 1
        else: gunluk_sayac[tarih][temiz_no] += 1
            
        tekrar = gunluk_sayac[tarih][temiz_no]
        
        sonuc.append({
            "genel_sira": s[0], 
            "gunluk_sira": s[1], 
            "telefon_no": temizle_ve_formatla(temiz_no), 
            "raw_phone": temiz_no, 
            "baslangic_zamani": s[3], 
            "bitis_zamani": s[4] if s[4] else "-", 
            "toplam_sure": s[5] if s[5] else 0, 
            "durum": s[6], 
            "notlar": s[7] if len(s)>7 and s[7] else "",
            "tekrar_sayisi": tekrar
        })
        
    sonuc.reverse() # Arayüze en yeni en üstte gidecek şekilde yolla
    return jsonify({"data": sonuc})

@app.route('/update_note', methods=['POST'])
def update_note():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE gorusmeler SET notlar = ? WHERE id = ?", (data.get('note', ''), data.get('id')))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/get_last_number', methods=['GET'])
def get_last_number():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, telefon_no FROM gorusmeler ORDER BY id DESC LIMIT 1")
    res = cursor.fetchone()
    conn.close()
    if res: 
        temiz_no = temizle_ve_formatla(res[1], sadece_temiz=True)
        return jsonify({"status": "success", "id": res[0], "phone": temiz_no})
    return jsonify({"status": "error", "message": "Kayıt yok."}), 404

def create_phone_icon(bg_color):
    image = Image.new('RGBA', (64, 64), color=(0,0,0,0))
    d = ImageDraw.Draw(image)
    d.ellipse((0, 0, 64, 64), fill=bg_color)
    d.arc((12, 16, 52, 48), start=180, end=0, fill='white', width=6)
    d.ellipse((8, 30, 24, 46), fill='white')
    d.ellipse((40, 30, 56, 46), fill='white')
    return image

def toggle_console(icon, item):
    global console_visible
    if not console_visible:
        ctypes.windll.kernel32.AllocConsole()
        sys.stdout = open('CONOUT$', 'w')
        sys.stderr = open('CONOUT$', 'w')
        console_visible = True
        log_yaz("=== SERVER LOG EKRANI AKTİF ===")
    else:
        ctypes.windll.kernel32.FreeConsole()
        console_visible = False

def quit_app(icon, item):
    icon.stop()
    os._exit(0)

def run_flask():
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)
        console_visible = False

    baslat_donanim()
    threading.Thread(target=run_flask, daemon=True).start()

    menu = pystray.Menu(
        pystray.MenuItem('Konsolu Göster / Gizle', toggle_console, default=True),
        pystray.MenuItem('Çıkış Yap', quit_app)
    )
    icon = pystray.Icon("Santral", create_phone_icon('#198754'), "Server: Santral", menu)
    icon.run()