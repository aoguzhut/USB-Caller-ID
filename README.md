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

Donanım
- Bu çalışma sırasında test ve geliştirme için kullanılan ana donanım:
	- USB Caller ID alıcısı (model/marka: C812A)
	- Geliştirme: Windows 10/11 çalıştıran PC
	- Opsiyonel: HID arayüzlü cihazlar ve USB bağlantısı

Kullanılan DLL'ler
- Projede kullanılan/bağlanan DLL'ler (varsa):
	- `cidshow_x64/*.dll` ve/veya `cidshow_x86/*.dll` (referans için `old/pyCidshow` içeriğine bakın)
	- Eğer özel SDK DLL'leri kullanıldıysa, örnek: `callerid_sdk.dll` (gerçek DLL adlarını buraya yazın)
	- SDK ve DLL dokümantasyonu için: https://www.sistemler.com/sdk/
Not: DLL'lerin platform ve mimariye göre (x86/x64) doğru klasöre konulduğundan emin olun.

Bilinen Hatalar ve Notlar
- `old/captures/analysis_summary.txt` gibi analizlerde raporlanan bazı durumlarda, veritabanı veya CSV'deki `durum` sütunundaki değerlerin tutarsız olabileceği gözlemlenmiştir. Bu şu anlama gelir:
	- `durum` sütunu bazen eksik veya hatalı formatlı olabilir.
	- Bu sütuna güvenen otomatik işleme/filtreleme adımları önce veri doğrulaması yapmalıdır.
	- Öneri: `durum` alanını normalize eden bir doğrulama/adım ekleyin veya eksik/yanlış kayıtları gözden geçirecek bir manuel inceleme adımı bırakın.

Sorular veya düzeltmeler için lütfen `README.md` üzerinden güncelleme isteği gönderin veya doğrudan proje sahibine danışın.
