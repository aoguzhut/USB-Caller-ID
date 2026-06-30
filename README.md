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

Donanım
- Bu çalışma sırasında test ve geliştirme için kullanılan ana donanım:
	- USB Caller ID alıcısı (model/marka: C812A)
	- Geliştirme: Windows 10/11 çalıştıran PC
	- Opsiyonel: HID arayüzlü cihazlar ve USB bağlantısı

Kullanılan DLL'ler
- Projede kullanılan/bağlanan DLL'ler:
	- `cidshow_x64/*.dll` veya `cidshow_x86/*.dll` gibi vendor DLL'leri
	- SDK ve DLL dokümantasyonu için: https://www.sistemler.com/sdk/
 
Bilinen Hatalar ve Notlar
- Proje ile ilgili yerel analiz özetleri veya ham yakalamalar, veritabanı veya CSV'deki `durum` sütunundaki değerlerin tutarsız olabileceği gözlemlenmiştir. Bu şu anlama gelir:
	- `durum` sütunu bazen eksik veya hatalı olabilir.
	- Bu sütuna güvenen otomatik işleme/filtreleme adımları önce veri doğrulaması yapmalıdır.

Sorular veya düzeltmeler için lütfen `README.md` üzerinden güncelleme isteği gönderin veya doğrudan proje sahibine danışın.
