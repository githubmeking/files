# Telegram Otomatik Veri Toplama Sistemi

Telegram grup ve kanallarından 7/24 otomatik veri toplama sistemi.

## Özellikler

- 70+ userbot hesabı desteği
- Grup ve kanal bilgilerini otomatik toplama
- Kurucu, yönetici, bot ve üye bilgileri
- Yetki ve izin bilgileri
- 7/24 sürekli tarama modu
- FloodWait otomatik yönetimi
- PostgreSQL veritabanı desteği

## Kurulum

### 1. Sistemi Güncelle
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. PostgreSQL Kur
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Veritabanı Oluştur
```bash
sudo -u postgres psql
```

PostgreSQL içinde:
```sql
CREATE DATABASE telegram_data;
CREATE USER telegram_user WITH PASSWORD 'güçlü_şifre_buraya';
GRANT ALL PRIVILEGES ON DATABASE telegram_data TO telegram_user;
\q
```

### 4. Python ve Paketleri Kur
```bash
sudo apt install python3 python3-pip python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Konfigürasyon
`.env` dosyasını düzenleyin:
```bash
nano .env
```

Database bilgilerinizi girin:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telegram_data
DB_USER=telegram_user
DB_PASSWORD=güçlü_şifre_buraya
```

## Kullanım

### Programı Başlat
```bash
source venv/bin/activate
python3 main.py
```

### Ana Menü

```
1. Hesap Ekle - Yeni userbot hesabı ekle
2. Kayıtlı Hesapları Listele - Tüm hesapları göster
3. Hesap Detaylarını Görüntüle - Hesap bilgilerini gör
4. Sıralı Veri Toplamaya Başlat - Tek seferlik tam tarama
5. Sıralı Veri Toplamayı Durdur - Taramayı durdur
6. Tüm İstatistikleri Görüntüle - Toplanan veri sayıları
7. Sadece Grupları Topla
8. Sadece Gruptaki İzinleri Topla
9. Sadece Gruptaki Kurucuları Topla
...
24. Sürekli Veri Toplamaya Başlat (7/24) - Otomatik döngü
25. Sürekli Veri Toplamayı Durdur
26. Çıkış
```

### Hesap Ekleme

1. Telegram API ID ve Hash alın: https://my.telegram.org
2. Menüden "1" seçin
3. API ID, API Hash, Telefon numarası girin
4. Telegram'dan gelen kodu girin
5. 2FA şifresi varsa girin

### Veri Toplama

**Tek Seferlik:**
- Seçenek 4: Tüm verileri tek seferde topla

**Sürekli Mod (7/24):**
- Seçenek 24: Her 10 dakikada bir otomatik tarama
- Seçenek 25: Durdurmak için

## Veritabanı Tabloları

### Hesaplar
- Userbot hesap bilgileri

### Gruplar
- Grup temel bilgileri
- grup_izinler: Grup izin ayarları
- grup_kurucular: Grup kurucuları
- grup_kurucu_yetkiler: Kurucu yetkileri
- grup_yoneticiler: Yöneticiler
- grup_yonetici_yetkiler: Yönetici yetkileri
- grup_botlar: Gruptaki botlar
- grup_bot_yetkiler: Bot yetkileri
- grup_uyeler: Grup üyeleri
- grup_istatistikler: Grup istatistikleri

### Kanallar
- Kanal temel bilgileri
- kanal_kurucular: Kanal kurucuları
- kanal_kurucu_yetkiler: Kurucu yetkileri
- kanal_yoneticiler: Yöneticiler
- kanal_yonetici_yetkiler: Yönetici yetkileri
- kanal_botlar: Kanaldaki botlar
- kanal_bot_yetkiler: Bot yetkileri
- kanal_uyeler: Kanal üyeleri
- kanal_istatistikler: Kanal istatistikleri

## FloodWait Yönetimi

Sistem otomatik olarak Telegram'ın rate limit'lerini yönetir:
- 100'er veri kaydeder
- FloodWait durumunda bekler
- 10 dakika aralıklarla tekrar tarar

## Güvenlik

- Session stringler database'de saklanır
- 2FA şifreleri şifreli tutulur
- Sadece yetkiniz olan gruplara erişilir

## Sorun Giderme

### Database bağlantı hatası
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT 1"
```

### Permission hatası
```bash
sudo -u postgres psql telegram_data -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO telegram_user;"
```

### FloodWait çok sık
- BATCH_SIZE değerini azaltın (.env)
- WAIT_TIME değerini artırın

## Notlar

- Telegram API limitlerine dikkat edin
- Çok fazla hesap kullanmayın (ban riski)
- Session dosyalarını yedekleyin
- Database'i düzenli yedekleyin

## Lisans

Bu proje MIT lisansı altındadır.
