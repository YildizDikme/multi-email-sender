# MailSender — Toplu E-posta Gönderici

CSV veya Excel dosyanı yükle, mesajını yaz, tek tıkla herkese gönder.

---

## Hızlı Başlangıç — 4 Adım

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. .env dosyasını oluştur
cp .env.example .env
# → .env dosyasını aç ve e-posta bilgilerini gir

# 3. Uygulamayı başlat
python app.py

# 4. Tarayıcıda aç
# http://localhost:5000
```

---

## .env Nasıl Doldurulur?

`.env.example` dosyasını `.env` adıyla kopyala ve şu alanları doldur:

| Alan | Açıklama |
|------|----------|
| `SMTP_USER` | Gönderen e-posta adresin |
| `SMTP_PASS` | Şifre veya App Password |
| `SMTP_FROM` | Gönderen adresi (genellikle `SMTP_USER` ile aynı) |

### Gmail kullanıyorsan:

Gmail normal şifreni **kabul etmez**. Bunun yerine "Uygulama Şifresi" lazım:

1. https://myaccount.google.com/security adresine git
2. **"2 Adımlı Doğrulama"** aç (açık değilse)
3. Sayfada **"Uygulama şifreleri"** ara
4. Uygulama: **Mail** → Cihaz: **Other** → bir isim ver → **Oluştur**
5. 16 haneli şifreyi `SMTP_PASS` alanına gir (boşluksuz)

### Outlook / Hotmail kullanıyorsan:

`SMTP_HOST=smtp.office365.com` ve `SMTP_PORT=587` yap, normal şifreni gir.

---

## CSV Formatı

Dosyanda en az bir **email** sütunu olmalı:

```csv
name,email
Ayşe Yılmaz,ayse@ornek.com
Mehmet Demir,mehmet@ornek.com
```

Desteklenen sütun adları:
- **E-posta:** `email`, `mail`, `e-posta`, `eposta`
- **Ad:** `name`, `isim`, `ad`, `fullname`

---

## Kişiselleştirilmiş Mesaj

Mesajda `{name}` veya `{isim}` yazarsan, her kişi için otomatik değiştirilir:

```
Merhaba {name},

Sana özel bir teklifimiz var...
```

---

## Yaygın Hatalar

**"SMTP ayarları eksik" hatası**
→ `.env` dosyasını oluşturdun mu? `SMTP_USER` ve `SMTP_PASS` boş bırakılamaz.

**"SMTP bağlantısı kurulamadı"**
→ Gmail kullanıyorsan App Password gerekli (normal şifre çalışmaz).
→ İnternet bağlantını kontrol et.

**"E-posta sütunu bulunamadı"**
→ CSV'deki sütun adını `email` veya `mail` olarak değiştir.

**Uygulama açılmıyor**
→ `pip install -r requirements.txt` çalıştırdın mı?

**Değişiklikler görünmüyor**
→ Sayfayı `Ctrl+Shift+R` ile yenile (cache temizleyerek).

---

## Komutlar

| İşlem | Mac/Linux | Windows |
|-------|-----------|---------|
| Kur | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Başlat | `python app.py` | `python app.py` |
