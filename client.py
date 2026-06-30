import requests
import time
import pyperclip
import threading
import pystray
from PIL import Image, ImageDraw
import os
import ctypes
import sys

SERVER_URL = "http://10.53.0.120:5001/get_last_number" 
last_call_id = None
console_visible = False

def log_yaz(mesaj):
    if console_visible:
        try:
            print(mesaj)
            sys.stdout.flush()
        except: pass

def auto_clipboard_service():
    global last_call_id
    
    try:
        init_req = requests.get(SERVER_URL, timeout=2)
        if init_req.status_code == 200:
            last_call_id = init_req.json().get("id")
    except: pass

    while True:
        try:
            response = requests.get(SERVER_URL, timeout=2)
            if response.status_code == 200:
                data = response.json()
                current_id = data.get("id")
                phone = data.get("phone", "")
                
                if current_id and current_id != last_call_id:
                    last_call_id = current_id
                    if phone:
                        pyperclip.copy(phone)
                        log_yaz(f"[{time.strftime('%H:%M:%S')}] YENİ ÇAĞRI PANOYA ALINDI: {phone}")
        except Exception: pass 
            
        time.sleep(1)

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
        log_yaz("=== CLIENT LOG EKRANI AKTİF ===")
        log_yaz("Otomatik kopyalama servisi devrede...")
    else:
        ctypes.windll.kernel32.FreeConsole()
        console_visible = False

def quit_app(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == "__main__":
    threading.Thread(target=auto_clipboard_service, daemon=True).start()

    menu = pystray.Menu(
        pystray.MenuItem('Konsolu Göster / Gizle', toggle_console, default=True),
        pystray.MenuItem('Çıkış', quit_app)
    )
    # Client için MAVİ telefon simgesi
    icon = pystray.Icon("Client", create_phone_icon('#0d6efd'), "Client: Kopyalayıcı", menu)
    icon.run()