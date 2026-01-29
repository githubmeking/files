import asyncpg
from config import Config
from datetime import datetime

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Database bağlantısı oluştur"""
        try:
            self.pool = await asyncpg.create_pool(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                min_size=5,
                max_size=20
            )
            print("✓ Veritabanına başarıyla bağlanıldı!")
            return True
        except Exception as e:
            print(f"✗ Veritabanı bağlantı hatası: {e}")
            return False
    
    async def disconnect(self):
        """Database bağlantısını kapat"""
        if self.pool:
            await self.pool.close()
            print("✓ Veritabanı bağlantısı kapatıldı!")
    
    async def create_tables(self):
        """Tüm tabloları oluştur"""
        if not self.pool:
            print("✗ Veritabanı bağlantısı yok!")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                # 1. HESAPLAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS hesaplar (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT UNIQUE,
                        api_id INTEGER,
                        api_hash TEXT,
                        telefon_no TEXT,
                        hesap_adi TEXT,
                        ad TEXT,
                        soyad TEXT,
                        kullanici_adi TEXT,
                        iki_faktorlu_kod TEXT,
                        session_string TEXT,
                        is_aktif BOOLEAN DEFAULT TRUE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 2. GRUPLAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS gruplar (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT UNIQUE,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        grup_link TEXT,
                        tur TEXT,
                        grup_aciklama TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        toplam_gorunen_uye INTEGER DEFAULT 0,
                        is_grup_gizli BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_aktif_kurucu BOOLEAN DEFAULT TRUE,
                        grup_kurulus_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 3. GRUP_IZINLER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_izinler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        can_send_messages BOOLEAN DEFAULT TRUE,
                        can_send_photos BOOLEAN DEFAULT TRUE,
                        can_send_videos BOOLEAN DEFAULT TRUE,
                        can_send_other_messages BOOLEAN DEFAULT TRUE,
                        can_send_audios BOOLEAN DEFAULT TRUE,
                        can_send_documents BOOLEAN DEFAULT TRUE,
                        can_send_voice_notes BOOLEAN DEFAULT TRUE,
                        can_send_video_notes BOOLEAN DEFAULT TRUE,
                        can_add_web_page_previews BOOLEAN DEFAULT TRUE,
                        can_send_polls BOOLEAN DEFAULT TRUE,
                        can_invite_users BOOLEAN DEFAULT TRUE,
                        can_pin_messages BOOLEAN DEFAULT TRUE,
                        can_change_info BOOLEAN DEFAULT TRUE,
                        can_send_stars BOOLEAN DEFAULT TRUE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id)
                    )
                ''')
                
                # 4. GRUP_KURUCULAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_kurucular (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        kurucu_about TEXT,
                        kurucu_telefon TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_aktif_kurucu BOOLEAN DEFAULT TRUE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, kurucu_id)
                    )
                ''')
                
                # 5. GRUP_KURUCU_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_kurucu_yetkiler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_pin_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        is_anonymous BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, kurucu_id)
                    )
                ''')
                
                # 6. GRUP_YONETICILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_yoneticiler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        rol TEXT,
                        yonetici_id BIGINT,
                        yonetici_adsoyad TEXT,
                        yonetici_kadi TEXT,
                        yonetici_aciklama TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        ekleyen_id BIGINT,
                        ekleyen_adsoyad TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_aktif_yonetici BOOLEAN DEFAULT TRUE,
                        yonetici_atama_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, yonetici_id)
                    )
                ''')
                
                # 7. GRUP_YONETICI_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_yonetici_yetkiler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        yonetici_id BIGINT,
                        yonetici_adsoyad TEXT,
                        yonetici_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_pin_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        is_anonymous BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        yonetici_atama_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, yonetici_id)
                    )
                ''')
                
                # 8. GRUP_BOTLAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_botlar (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        rol TEXT,
                        bot_id BIGINT,
                        bot_adsoyad TEXT,
                        bot_kadi TEXT,
                        bot_about TEXT,
                        ekleyen_id BIGINT,
                        ekleyen_adsoyad TEXT,
                        is_yonetici BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT TRUE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, bot_id)
                    )
                ''')
                
                # 9. GRUP_BOT_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_bot_yetkiler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        bot_id BIGINT,
                        bot_adsoyad TEXT,
                        bot_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_pin_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        is_anonymous BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        bot_atama_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, bot_id)
                    )
                ''')
                
                # 10. GRUP_UYELER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_uyeler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        uye_id BIGINT,
                        uye_adsoyad TEXT,
                        uye_kadi TEXT,
                        uye_aciklama TEXT,
                        uye_telefon TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_kurucu BOOLEAN DEFAULT FALSE,
                        is_yonetici BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_aktif_uye BOOLEAN DEFAULT TRUE,
                        uye_katilma_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(grup_id, uye_id)
                    )
                ''')
                
                # 11. GRUP_ISTATISTIKLER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS grup_istatistikler (
                        id SERIAL PRIMARY KEY,
                        grup_id BIGINT UNIQUE,
                        grup_name TEXT,
                        grup_kadi TEXT,
                        tur TEXT,
                        grup_gorunen_sayi INTEGER DEFAULT 0,
                        toplam_kurucu INTEGER DEFAULT 0,
                        toplam_yonetici INTEGER DEFAULT 0,
                        toplam_bot INTEGER DEFAULT 0,
                        toplam_uye INTEGER DEFAULT 0,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 12. KANALLAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanallar (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT UNIQUE,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        kanal_link TEXT,
                        tur TEXT,
                        kanal_aciklama TEXT,
                        toplam_gorunen_uye INTEGER DEFAULT 0,
                        is_kanal_gizli BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_kurucu BOOLEAN DEFAULT TRUE,
                        kanal_kurulus_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 13. KANAL_KURUCULAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_kurucular (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        kurucu_aciklama TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_kurucu BOOLEAN DEFAULT TRUE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, kurucu_id)
                    )
                ''')
                
                # 14. KANAL_KURUCU_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_kurucu_yetkiler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        kurucu_id BIGINT,
                        kurucu_adsoyad TEXT,
                        kurucu_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_manage_messages BOOLEAN DEFAULT FALSE,
                        can_post_messages BOOLEAN DEFAULT FALSE,
                        can_edit_messages BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_manage_chat BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, kurucu_id)
                    )
                ''')
                
                # 15. KANAL_YONETICILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_yoneticiler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        yonetici_id BIGINT,
                        yonetici_adsoyad TEXT,
                        yonetici_kadi TEXT,
                        yonetici_aciklama TEXT,
                        yonetici_phone TEXT,
                        ekleyen_id BIGINT,
                        ekleyen_adsoyad TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_kurucu BOOLEAN DEFAULT FALSE,
                        is_yonetici BOOLEAN DEFAULT TRUE,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, yonetici_id)
                    )
                ''')
                
                # 16. KANAL_YONETICI_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_yonetici_yetkiler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        yonetici_id BIGINT,
                        yonetici_adsoyad TEXT,
                        yonetici_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_manage_messages BOOLEAN DEFAULT FALSE,
                        can_post_messages BOOLEAN DEFAULT FALSE,
                        can_edit_messages BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_manage_chat BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        yonetici_atama_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, yonetici_id)
                    )
                ''')
                
                # 17. KANAL_BOTLAR TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_botlar (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        bot_id BIGINT,
                        bot_adsoyad TEXT,
                        bot_kadi TEXT,
                        bot_aciklama TEXT,
                        ekleyen_id BIGINT,
                        ekleyen_adsoyad TEXT,
                        is_yonetici BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT TRUE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, bot_id)
                    )
                ''')
                
                # 18. KANAL_BOT_YETKILER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_bot_yetkiler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        bot_id BIGINT,
                        bot_adsoyad TEXT,
                        bot_kadi TEXT,
                        can_change_info BOOLEAN DEFAULT FALSE,
                        can_manage_messages BOOLEAN DEFAULT FALSE,
                        can_post_messages BOOLEAN DEFAULT FALSE,
                        can_edit_messages BOOLEAN DEFAULT FALSE,
                        can_delete_messages BOOLEAN DEFAULT FALSE,
                        can_manage_stories BOOLEAN DEFAULT FALSE,
                        can_post_stories BOOLEAN DEFAULT FALSE,
                        can_edit_stories BOOLEAN DEFAULT FALSE,
                        can_delete_stories BOOLEAN DEFAULT FALSE,
                        can_restrict_members BOOLEAN DEFAULT FALSE,
                        can_invite_users BOOLEAN DEFAULT FALSE,
                        can_manage_chat BOOLEAN DEFAULT FALSE,
                        can_manage_video_chats BOOLEAN DEFAULT FALSE,
                        can_promote_members BOOLEAN DEFAULT FALSE,
                        bot_atama_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, bot_id)
                    )
                ''')
                
                # 19. KANAL_UYELER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_uyeler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        uye_id BIGINT,
                        uye_adsoyad TEXT,
                        uye_kadi TEXT,
                        uye_aciklama TEXT,
                        uye_telefon TEXT,
                        is_premium BOOLEAN DEFAULT FALSE,
                        is_kurucu BOOLEAN DEFAULT FALSE,
                        is_yonetici BOOLEAN DEFAULT FALSE,
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_deleted BOOLEAN DEFAULT FALSE,
                        is_aktif_uye BOOLEAN DEFAULT TRUE,
                        uye_katilma_tarih TIMESTAMP,
                        kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(kanal_id, uye_id)
                    )
                ''')
                
                # 20. KANAL_ISTATISTIKLER TABLOSU
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS kanal_istatistikler (
                        id SERIAL PRIMARY KEY,
                        kanal_id BIGINT UNIQUE,
                        kanal_name TEXT,
                        kanal_kadi TEXT,
                        tur TEXT,
                        toplam_kanal_abone INTEGER DEFAULT 0,
                        toplam_kurucu INTEGER DEFAULT 0,
                        toplam_yonetici INTEGER DEFAULT 0,
                        toplam_bot INTEGER DEFAULT 0,
                        toplam_uye INTEGER DEFAULT 0,
                        guncel_tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                print("✓ Tüm tablolar başarıyla oluşturuldu!")
                return True
                
        except Exception as e:
            print(f"✗ Tablo oluşturma hatası: {e}")
            return False
    
    async def get_connection(self):
        """Bağlantı döndür"""
        if self.pool:
            return await self.pool.acquire()
        return None
