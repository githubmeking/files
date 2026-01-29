#!/bin/bash

echo "================================================"
echo "Telegram Otomatik Veri Toplama Sistemi Kurulumu"
echo "================================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗ Bu scripti root olarak çalıştırmalısınız${NC}"
    echo "Lütfen şunu kullanın: sudo bash setup.sh"
    exit 1
fi

echo -e "${GREEN}✓ Root erişimi doğrulandı${NC}"
echo ""

# Sistem güncelleme
echo -e "${YELLOW}Sistem güncelleniyor...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✓ Sistem güncellendi${NC}"
echo ""

# PostgreSQL kurulumu
echo -e "${YELLOW}PostgreSQL kuruluyor...${NC}"
apt install postgresql postgresql-contrib -y
systemctl start postgresql
systemctl enable postgresql
echo -e "${GREEN}✓ PostgreSQL kuruldu${NC}"
echo ""

# Python kurulumu
echo -e "${YELLOW}Python ve gerekli paketler kuruluyor...${NC}"
apt install python3 python3-pip python3-venv -y
echo -e "${GREEN}✓ Python kuruldu${NC}"
echo ""

# Veritabanı oluşturma
echo -e "${YELLOW}Veritabanı oluşturuluyor...${NC}"
echo "Lütfen veritabanı için bir şifre belirleyin:"
read -sp "PostgreSQL Şifresi: " DB_PASSWORD
echo ""

# PostgreSQL kullanıcısı ve veritabanı oluştur
sudo -u postgres psql << EOF
CREATE DATABASE telegram_data;
CREATE USER telegram_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE telegram_data TO telegram_user;
\c telegram_data
GRANT ALL ON SCHEMA public TO telegram_user;
EOF

echo -e "${GREEN}✓ Veritabanı oluşturuldu${NC}"
echo ""

# .env dosyasını güncelle
echo -e "${YELLOW}.env dosyası güncelleniyor...${NC}"
cat > .env << EOF
# PostgreSQL Database Konfigürasyonu
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telegram_data
DB_USER=telegram_user
DB_PASSWORD=$DB_PASSWORD

# Tarama Ayarları
BATCH_SIZE=100
WAIT_TIME=600
FLOOD_WAIT_TIME=60
EOF

echo -e "${GREEN}✓ .env dosyası güncellendi${NC}"
echo ""

# Virtual environment oluştur
echo -e "${YELLOW}Python virtual environment oluşturuluyor...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment oluşturuldu${NC}"
echo ""

# Python paketlerini kur
echo -e "${YELLOW}Python paketleri kuruluyor...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Python paketleri kuruldu${NC}"
echo ""

# Başlatma scripti oluştur
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 main.py
EOF

chmod +x start.sh

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Kurulum Tamamlandı!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Kullanım:${NC}"
echo "1. Telegram API bilgilerinizi hazırlayın (https://my.telegram.org)"
echo "2. Programı başlatın: ./start.sh"
echo "3. Menüden '1' seçerek hesap ekleyin"
echo "4. Veri toplamaya başlayın!"
echo ""
echo -e "${YELLOW}Önemli Notlar:${NC}"
echo "- Database şifreniz: $DB_PASSWORD"
echo "- Bu şifreyi güvenli bir yerde saklayın"
echo "- Session dosyalarını yedeklemeyi unutmayın"
echo ""
echo -e "${GREEN}İyi kullanımlar!${NC}"
