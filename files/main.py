import asyncio
import sys
from datetime import datetime
from pyrogram import Client, filters, types
from pyrogram.errors import (
    FloodWait, UserDeactivated, UserDeactivatedBan,
    PeerIdInvalid, ChannelPrivate, ChatAdminRequired
)
from config import Config
from database import Database
from colorama import Fore, Style, init
import os

# Colorama başlat
init(autoreset=True)

# Global değişkenler
db = Database()
clients = {}
is_scanning = False
stop_scanning = False

def print_header():
    """Ana menü başlığını yazdır"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + Style.BRIGHT + "TELEGRAM OTOMATİK VERİ TOPLAMA SİSTEMİ".center(60))
    print(Fore.CYAN + "=" * 60)

def print_menu():
    """Ana menüyü yazdır"""
    print_header()
    print(Fore.YELLOW + "\n1.  Hesap Ekle")
    print("2.  Kayıtlı Hesapları Listele")
    print("3.  Hesap Detaylarını Görüntüle")
    print("4.  Sıralı Veri Toplamaya Başlat (Tüm Roller – Userbot Dahil)")
    print("5.  Sıralı Veri Toplamayı Durdur")
    print("6.  Tüm İstatistikleri Görüntüle")
    print("7.  Sadece Grupları Topla")
    print("8.  Sadece Gruptaki İzinleri Topla")
    print("9.  Sadece Gruptaki Kurucuları Topla")
    print("10. Sadece Gruptaki Kurucunun Yetkilerini Topla")
    print("11. Sadece Gruptaki Yöneticileri Topla")
    print("12. Sadece Gruptaki Yöneticilerinin Yetkilerini Topla")
    print("13. Sadece Gruptaki Botları Topla")
    print("14. Sadece Gruptaki Botların Yetkilerini Topla")
    print("15. Sadece Gruplardaki Üyeleri Topla")
    print("16. Sadece Kanalları Topla")
    print("17. Sadece Kanaldaki Kurucuları Topla")
    print("18. Sadece Kanaldaki Kurucunun Yetkilerini Topla")
    print("19. Sadece Kanaldaki Yöneticileri Topla")
    print("20. Sadece Kanaldaki Yöneticilerinin Yetkilerini Topla")
    print("21. Sadece Kanaldaki Botları Topla")
    print("22. Sadece Kanaldaki Botların Yetkilerini Topla")
    print("23. Sadece Kanaldaki Üyelerini Topla")
    print("24. Sürekli Veri Toplamaya Başlat (7/24)")
    print("25. Sürekli Veri Toplamayı Durdur")
    print("26. Çıkış")
    print(Fore.CYAN + "=" * 60)

async def add_account():
    """Yeni hesap ekle"""
    print_header()
    print(Fore.GREEN + "\n=== YENİ HESAP EKLE ===\n")
    
    try:
        api_id = int(input("API ID: "))
        api_hash = input("API Hash: ")
        phone = input("Telefon No (+90...): ")
        two_factor = input("İki Faktörlü Şifre (varsa): ")
        
        # Pyrogram client oluştur
        client = Client(
            f"session_{phone}",
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone
        )
        
        print(Fore.YELLOW + "\n✓ Telegram'a bağlanılıyor...")
        await client.start()
        
        me = await client.get_me()
        
        # Session string al
        session_string = await client.export_session_string()
        
        # Database'e kaydet
        async with db.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO hesaplar (
                    telegram_id, api_id, api_hash, telefon_no,
                    hesap_adi, ad, soyad, kullanici_adi,
                    iki_faktorlu_kod, session_string, is_aktif
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (telegram_id) DO UPDATE SET
                    api_id = $2,
                    api_hash = $3,
                    telefon_no = $4,
                    hesap_adi = $5,
                    ad = $6,
                    soyad = $7,
                    kullanici_adi = $8,
                    iki_faktorlu_kod = $9,
                    session_string = $10,
                    is_aktif = $11
            ''', me.id, api_id, api_hash, phone,
                f"{me.first_name or ''} {me.last_name or ''}".strip(),
                me.first_name or '', me.last_name or '', me.username or '',
                two_factor, session_string, True)
        
        await client.stop()
        
        print(Fore.GREEN + f"\n✓ Hesap başarıyla eklendi!")
        print(f"  - Telegram ID: {me.id}")
        print(f"  - Ad Soyad: {me.first_name or ''} {me.last_name or ''}")
        print(f"  - Kullanıcı Adı: @{me.username or 'Yok'}")
        
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def list_accounts():
    """Kayıtlı hesapları listele"""
    print_header()
    print(Fore.GREEN + "\n=== KAYITLI HESAPLAR ===\n")
    
    try:
        async with db.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT telegram_id, hesap_adi, telefon_no, kullanici_adi, is_aktif
                FROM hesaplar
                ORDER BY id
            ''')
            
            if not rows:
                print(Fore.YELLOW + "Kayıtlı hesap bulunamadı.")
            else:
                print(f"{'ID':<15} {'Ad Soyad':<25} {'Telefon':<15} {'Kullanıcı Adı':<20} {'Durum'}")
                print("-" * 90)
                for row in rows:
                    status = Fore.GREEN + "Aktif" if row['is_aktif'] else Fore.RED + "Pasif"
                    print(f"{row['telegram_id']:<15} {row['hesap_adi']:<25} {row['telefon_no']:<15} @{row['kullanici_adi'] or 'Yok':<19} {status}")
                
                print(f"\n{Fore.CYAN}Toplam: {len(rows)} hesap")
    
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def show_account_details():
    """Hesap detaylarını göster"""
    print_header()
    print(Fore.GREEN + "\n=== HESAP DETAYLARI ===\n")
    
    try:
        telegram_id = int(input("Telegram ID: "))
        
        async with db.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM hesaplar WHERE telegram_id = $1
            ''', telegram_id)
            
            if not row:
                print(Fore.RED + "\n✗ Hesap bulunamadı!")
            else:
                print(Fore.CYAN + "\n" + "=" * 60)
                print(f"Telegram ID      : {row['telegram_id']}")
                print(f"API ID           : {row['api_id']}")
                print(f"API Hash         : {row['api_hash'][:20]}...")
                print(f"Telefon No       : {row['telefon_no']}")
                print(f"Hesap Adı        : {row['hesap_adi']}")
                print(f"Ad               : {row['ad']}")
                print(f"Soyad            : {row['soyad']}")
                print(f"Kullanıcı Adı    : @{row['kullanici_adi'] or 'Yok'}")
                print(f"2FA Kodu         : {'Var' if row['iki_faktorlu_kod'] else 'Yok'}")
                print(f"Durum            : {'Aktif' if row['is_aktif'] else 'Pasif'}")
                print(f"Kayıt Tarihi     : {row['kayit_tarihi']}")
                print(Fore.CYAN + "=" * 60)
    
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def load_all_clients():
    """Tüm hesapları yükle"""
    global clients
    
    try:
        async with db.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM hesaplar WHERE is_aktif = TRUE AND is_deleted = FALSE
            ''')
            
            print(Fore.YELLOW + f"\n✓ {len(rows)} aktif hesap yükleniyor...")
            
            for row in rows:
                try:
                    client = Client(
                        f"session_{row['telefon_no']}",
                        api_id=row['api_id'],
                        api_hash=row['api_hash'],
                        session_string=row['session_string']
                    )
                    
                    await client.start()
                    clients[row['telegram_id']] = client
                    print(Fore.GREEN + f"  ✓ {row['hesap_adi']} bağlandı")
                    
                except Exception as e:
                    print(Fore.RED + f"  ✗ {row['hesap_adi']} bağlanırken hata: {e}")
            
            print(Fore.GREEN + f"\n✓ Toplam {len(clients)} hesap başarıyla yüklendi!")
            return True
            
    except Exception as e:
        print(Fore.RED + f"\n✗ Hesap yükleme hatası: {e}")
        return False

async def stop_all_clients():
    """Tüm clientları durdur"""
    global clients
    
    print(Fore.YELLOW + "\n✓ Hesaplar kapatılıyor...")
    for telegram_id, client in clients.items():
        try:
            await client.stop()
        except:
            pass
    
    clients = {}
    print(Fore.GREEN + "✓ Tüm hesaplar kapatıldı!")

def get_full_name(user):
    """Kullanıcının tam adını al"""
    if not user:
        return "Bilinmiyor"
    
    first_name = user.first_name or ""
    last_name = user.last_name or ""
    return f"{first_name} {last_name}".strip() or "Adsız"

def get_username(user):
    """Kullanıcı adını al"""
    if not user:
        return None
    return user.username

def get_chat_type(chat):
    """Chat türünü belirle"""
    if chat.type == types.enums.ChatType.SUPERGROUP:
        return "Süper Grup"
    elif chat.type == types.enums.ChatType.GROUP:
        return "Grup"
    elif chat.type == types.enums.ChatType.CHANNEL:
        return "Kanal"
    else:
        return "Bilinmiyor"

async def get_chat_link(client, chat):
    """Chat linkini al"""
    try:
        if chat.username:
            return f"https://t.me/{chat.username}"
        else:
            # Gizli grup/kanal için davet linki al
            chat_full = await client.get_chat(chat.id)
            if hasattr(chat_full, 'invite_link') and chat_full.invite_link:
                return chat_full.invite_link
            else:
                # Yöneticiyse link oluştur
                try:
                    link = await client.export_chat_invite_link(chat.id)
                    return link
                except:
                    return "Link alınamadı"
    except:
        return "Link alınamadı"

async def get_creation_date(client, chat_id):
    """Grup/kanal oluşturulma tarihini al"""
    try:
        # İlk mesajı bul
        async for message in client.get_chat_history(chat_id, limit=1, offset=-1):
            return message.date
    except:
        pass
    return None

async def collect_groups():
    """Grupları topla"""
    print_header()
    print(Fore.GREEN + "\n=== GRUPLARI TOPLAMA ===\n")
    
    if not clients:
        if not await load_all_clients():
            return
    
    try:
        collected_groups = set()
        total_saved = 0
        
        for telegram_id, client in clients.items():
            try:
                print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için gruplar taranıyor...")
                
                async for dialog in client.get_dialogs():
                    if stop_scanning:
                        print(Fore.RED + "\n✗ Tarama durduruldu!")
                        return
                    
                    chat = dialog.chat
                    
                    # Sadece grup ve süper grupları al
                    if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                        continue
                    
                    # Zaten kaydedilmiş mi kontrol et
                    if chat.id in collected_groups:
                        continue
                    
                    try:
                        # Grup detaylarını al
                        chat_full = await client.get_chat(chat.id)
                        
                        # Kurucu bilgilerini bul
                        creator_id = None
                        creator_name = None
                        creator_username = None
                        is_creator_active = False
                        
                        try:
                            async for member in client.get_chat_members(chat.id, filter=types.enums.ChatMembersFilter.ADMINISTRATORS):
                                if isinstance(member, types.ChatMember):
                                    if member.status == types.enums.ChatMemberStatus.OWNER:
                                        creator_id = member.user.id
                                        creator_name = get_full_name(member.user)
                                        creator_username = get_username(member.user)
                                        is_creator_active = True
                                        break
                        except:
                            pass
                        
                        # Database'e kaydet
                        async with db.pool.acquire() as conn:
                            await conn.execute('''
                                INSERT INTO gruplar (
                                    grup_id, grup_name, grup_kadi, grup_link, tur,
                                    grup_aciklama, kurucu_id, kurucu_adsoyad, kurucu_kadi,
                                    toplam_gorunen_uye, is_grup_gizli, is_deleted,
                                    is_aktif_kurucu, grup_kurulus_tarih, guncel_tarih
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                                ON CONFLICT (grup_id) DO UPDATE SET
                                    grup_name = $2,
                                    grup_kadi = $3,
                                    grup_link = $4,
                                    grup_aciklama = $6,
                                    kurucu_id = $7,
                                    kurucu_adsoyad = $8,
                                    kurucu_kadi = $9,
                                    toplam_gorunen_uye = $10,
                                    is_grup_gizli = $11,
                                    is_aktif_kurucu = $13,
                                    guncel_tarih = $15
                            ''', chat.id, chat.title, chat.username,
                                await get_chat_link(client, chat),
                                get_chat_type(chat),
                                chat_full.description or "",
                                creator_id, creator_name, creator_username,
                                chat.members_count or 0,
                                chat.username is None,
                                False,
                                is_creator_active,
                                await get_creation_date(client, chat.id),
                                datetime.now())
                        
                        collected_groups.add(chat.id)
                        total_saved += 1
                        print(Fore.GREEN + f"  ✓ {chat.title} kaydedildi ({total_saved})")
                        
                        await asyncio.sleep(0.5)  # Rate limit
                        
                    except FloodWait as e:
                        print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye bekleniyor...")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        print(Fore.RED + f"  ✗ {chat.title} kaydedilemedi: {e}")
                        continue
                
            except Exception as e:
                print(Fore.RED + f"✗ {telegram_id} hesabı taranırken hata: {e}")
                continue
        
        print(Fore.GREEN + f"\n✓ Toplam {total_saved} grup başarıyla kaydedildi!")
        
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def collect_group_permissions():
    """Grup izinlerini topla"""
    print_header()
    print(Fore.GREEN + "\n=== GRUP İZİNLERİNİ TOPLAMA ===\n")
    
    if not clients:
        if not await load_all_clients():
            return
    
    try:
        total_saved = 0
        
        for telegram_id, client in clients.items():
            try:
                print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için grup izinleri taranıyor...")
                
                async for dialog in client.get_dialogs():
                    if stop_scanning:
                        print(Fore.RED + "\n✗ Tarama durduruldu!")
                        return
                    
                    chat = dialog.chat
                    
                    if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                        continue
                    
                    try:
                        # İzinleri al
                        chat_full = await client.get_chat(chat.id)
                        perms = chat_full.permissions
                        
                        # Kurucu bilgisi
                        creator_id = None
                        creator_name = None
                        creator_username = None
                        
                        try:
                            async for member in client.get_chat_members(chat.id, filter=types.enums.ChatMembersFilter.ADMINISTRATORS):
                                if member.status == types.enums.ChatMemberStatus.OWNER:
                                    creator_id = member.user.id
                                    creator_name = get_full_name(member.user)
                                    creator_username = get_username(member.user)
                                    break
                        except:
                            pass
                        
                        # Database'e kaydet
                        async with db.pool.acquire() as conn:
                            await conn.execute('''
                                INSERT INTO grup_izinler (
                                    grup_id, grup_name, grup_kadi, tur,
                                    kurucu_id, kurucu_adsoyad, kurucu_kadi,
                                    can_send_messages, can_send_photos, can_send_videos,
                                    can_send_other_messages, can_send_audios, can_send_documents,
                                    can_send_voice_notes, can_send_video_notes,
                                    can_add_web_page_previews, can_send_polls,
                                    can_invite_users, can_pin_messages, can_change_info,
                                    guncel_tarih
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21)
                                ON CONFLICT (grup_id) DO UPDATE SET
                                    grup_name = $2,
                                    can_send_messages = $8,
                                    can_send_photos = $9,
                                    can_send_videos = $10,
                                    can_send_other_messages = $11,
                                    can_send_audios = $12,
                                    can_send_documents = $13,
                                    can_send_voice_notes = $14,
                                    can_send_video_notes = $15,
                                    can_add_web_page_previews = $16,
                                    can_send_polls = $17,
                                    can_invite_users = $18,
                                    can_pin_messages = $19,
                                    can_change_info = $20,
                                    guncel_tarih = $21
                            ''', chat.id, chat.title, chat.username, get_chat_type(chat),
                                creator_id, creator_name, creator_username,
                                perms.can_send_messages if perms else True,
                                perms.can_send_photos if perms else True,
                                perms.can_send_videos if perms else True,
                                perms.can_send_other_messages if perms else True,
                                perms.can_send_audios if perms else True,
                                perms.can_send_documents if perms else True,
                                perms.can_send_voice_notes if perms else True,
                                perms.can_send_video_notes if perms else True,
                                perms.can_add_web_page_previews if perms else True,
                                perms.can_send_polls if perms else True,
                                perms.can_invite_users if perms else True,
                                perms.can_pin_messages if perms else True,
                                perms.can_change_info if perms else True,
                                datetime.now())
                        
                        total_saved += 1
                        print(Fore.GREEN + f"  ✓ {chat.title} izinleri kaydedildi ({total_saved})")
                        
                        await asyncio.sleep(0.5)
                        
                    except FloodWait as e:
                        print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye bekleniyor...")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        print(Fore.RED + f"  ✗ {chat.title} izinleri kaydedilemedi: {e}")
                        continue
                
            except Exception as e:
                print(Fore.RED + f"✗ {telegram_id} hesabı taranırken hata: {e}")
                continue
        
        print(Fore.GREEN + f"\n✓ Toplam {total_saved} grup izni başarıyla kaydedildi!")
        
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def show_statistics():
    """İstatistikleri göster"""
    print_header()
    print(Fore.GREEN + "\n=== İSTATİSTİKLER ===\n")
    
    try:
        async with db.pool.acquire() as conn:
            hesap_count = await conn.fetchval('SELECT COUNT(*) FROM hesaplar WHERE is_aktif = TRUE')
            grup_count = await conn.fetchval('SELECT COUNT(*) FROM gruplar')
            grup_izin_count = await conn.fetchval('SELECT COUNT(*) FROM grup_izinler')
            grup_kurucu_count = await conn.fetchval('SELECT COUNT(*) FROM grup_kurucular')
            grup_yonetici_count = await conn.fetchval('SELECT COUNT(*) FROM grup_yoneticiler')
            grup_bot_count = await conn.fetchval('SELECT COUNT(*) FROM grup_botlar')
            grup_uye_count = await conn.fetchval('SELECT COUNT(*) FROM grup_uyeler')
            kanal_count = await conn.fetchval('SELECT COUNT(*) FROM kanallar')
            kanal_kurucu_count = await conn.fetchval('SELECT COUNT(*) FROM kanal_kurucular')
            kanal_yonetici_count = await conn.fetchval('SELECT COUNT(*) FROM kanal_yoneticiler')
            kanal_bot_count = await conn.fetchval('SELECT COUNT(*) FROM kanal_botlar')
            kanal_uye_count = await conn.fetchval('SELECT COUNT(*) FROM kanal_uyeler')
            
            print(Fore.CYAN + "=" * 60)
            print(Fore.YELLOW + "\nHESAPLAR:")
            print(f"  Aktif Hesap: {hesap_count}")
            print(Fore.YELLOW + "\nGRUP İSTATİSTİKLERİ:")
            print(f"  Toplam Grup: {grup_count}")
            print(f"  İzinler: {grup_izin_count}")
            print(f"  Kurucular: {grup_kurucu_count}")
            print(f"  Yöneticiler: {grup_yonetici_count}")
            print(f"  Botlar: {grup_bot_count}")
            print(f"  Üyeler: {grup_uye_count}")
            print(Fore.YELLOW + "\nKANAL İSTATİSTİKLERİ:")
            print(f"  Toplam Kanal: {kanal_count}")
            print(f"  Kurucular: {kanal_kurucu_count}")
            print(f"  Yöneticiler: {kanal_yonetici_count}")
            print(f"  Botlar: {kanal_bot_count}")
            print(f"  Üyeler: {kanal_uye_count}")
            print(Fore.CYAN + "=" * 60)
    except Exception as e:
        print(Fore.RED + f"\n✗ Hata: {e}")
    input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

async def main():
    """Ana program"""
    global db
    print_header()
    print(Fore.GREEN + "\nSisteme hoş geldiniz!")
    if not await db.connect():
        print(Fore.RED + "✗ Veritabanına bağlanılamadı!")
        return
    await db.create_tables()
    
    while True:
        try:
            print_menu()
            choice = input(Fore.YELLOW + "\nSeçiminiz [1-26]: ").strip()
            
            if choice == '1':
                await add_account()
            elif choice == '2':
                await list_accounts()
            elif choice == '3':
                await show_account_details()
            elif choice == '6':
                await show_statistics()
            elif choice == '7':
                await collect_groups()
            elif choice == '8':
                await collect_group_permissions()
            elif choice == '26':
                print(Fore.GREEN + "\nÇıkış yapılıyor...")
                await stop_all_clients()
                await db.disconnect()
                break
            else:
                print(Fore.YELLOW + f"\n✓ Seçenek {choice} - Yakında aktif olacak")
                input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\nProgram sonlandırılıyor...")
            await stop_all_clients()
            await db.disconnect()
            break
        except Exception as e:
            print(Fore.RED + f"\n✗ Hata: {e}")
            input(Fore.YELLOW + "\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nProgram sonlandırıldı!")
