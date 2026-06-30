# CallerID

Basit bir Caller ID örnek projesi — `server.py` ve `client.py` içerir. Proje, PyInstaller ile paketlenmiş örnek build çıktılarını da içerebilir (ör. `build/` klasörü).

Prerequisites
- Python 3.8 veya üzeri
- (Tercihen) sanal ortam: `python -m venv .venv`

Hızlı Başlangıç
1. Sanal ortam oluşturun ve etkinleştirin (PowerShell için):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Gerekli paketler varsa yükleyin:

```powershell
pip install -r requirements.txt
```

3. Sunucuyu çalıştırın:

```powershell
python server.py
```

4. İstemciyi çalıştırın:

```powershell
python client.py
```

Derleme (opsiyonel)
- PyInstaller kullanarak `server.spec` veya `client.spec` ile paketleyebilirsiniz:

```powershell
pyinstaller server.spec
pyinstaller client.spec
```

Notlar
- Hazır build çıktıları `build/` klasöründe bulunabilir; bu klasörü repoda takip etmiyorsanız `.gitignore` zaten ihmal eder.
- Eski, referans amaçlı dosyalar `old/` klasöründe tutulmuştur.

Lisans
- Bu depo için lisans belirtilmemiştir; eklemek isterseniz uygun lisans dosyasını (`LICENSE`) ekleyin.
