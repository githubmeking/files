"""
Telegram Veri Toplama Fonksiyonları
"""
import asyncio
from datetime import datetime
from pyrogram import types
from pyrogram.errors import FloodWait
from colorama import Fore

async def collect_group_creators(clients, db, stop_scanning):
    """Grup kurucularını topla"""
    print(Fore.GREEN + "\n=== GRUP KURUCULARINI TOPLAMA ===\n")
    
    total_saved = 0
    
    for telegram_id, client in clients.items():
        try:
            print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için grup kurucuları taranıyor...")
            
            async for dialog in client.get_dialogs():
                if stop_scanning:
                    return total_saved
                
                chat = dialog.chat
                
                if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                    continue
                
                try:
                    async for member in client.get_chat_members(chat.id, filter=types.enums.ChatMembersFilter.ADMINISTRATORS):
                        if member.status == types.enums.ChatMemberStatus.OWNER:
                            user = member.user
                            
                            # Kullanıcı bilgilerini al
                            try:
                                user_full = await client.get_users(user.id)
                                about = user_full.about if hasattr(user_full, 'about') else ""
                                phone = user_full.phone_number if hasattr(user_full, 'phone_number') else ""
                            except:
                                about = ""
                                phone = ""
                            
                            async with db.pool.acquire() as conn:
                                await conn.execute('''
                                    INSERT INTO grup_kurucular (
                                        grup_id, grup_name, grup_kadi, tur,
                                        kurucu_id, kurucu_adsoyad, kurucu_kadi,
                                        kurucu_about, kurucu_telefon, is_premium,
                                        is_bot, is_deleted, is_aktif_kurucu, guncel_tarih
                                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                                    ON CONFLICT (grup_id, kurucu_id) DO UPDATE SET
                                        grup_name = $2,
                                        kurucu_adsoyad = $6,
                                        kurucu_about = $8,
                                        is_premium = $10,
                                        is_aktif_kurucu = $13,
                                        guncel_tarih = $14
                                ''', chat.id, chat.title, chat.username,
                                    "Süper Grup" if chat.type == types.enums.ChatType.SUPERGROUP else "Grup",
                                    user.id,
                                    f"{user.first_name or ''} {user.last_name or ''}".strip(),
                                    user.username,
                                    about, phone,
                                    user.is_premium or False,
                                    user.is_bot,
                                    False,
                                    True,
                                    datetime.now())
                            
                            total_saved += 1
                            print(Fore.GREEN + f"  ✓ {chat.title} kurucusu kaydedildi")
                            break
                    
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    continue
        
        except Exception as e:
            print(Fore.RED + f"✗ Hata: {e}")
            continue
    
    return total_saved

async def collect_group_admins(clients, db, stop_scanning):
    """Grup yöneticilerini topla"""
    print(Fore.GREEN + "\n=== GRUP YÖNETİCİLERİNİ TOPLAMA ===\n")
    
    total_saved = 0
    
    for telegram_id, client in clients.items():
        try:
            print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için yöneticiler taranıyor...")
            
            async for dialog in client.get_dialogs():
                if stop_scanning:
                    return total_saved
                
                chat = dialog.chat
                
                if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                    continue
                
                try:
                    # Kurucu bilgisi
                    creator_id = None
                    creator_name = None
                    
                    async for member in client.get_chat_members(chat.id, filter=types.enums.ChatMembersFilter.ADMINISTRATORS):
                        user = member.user
                        
                        # Kurucu ve bot değilse
                        if member.status == types.enums.ChatMemberStatus.OWNER or user.is_bot:
                            if member.status == types.enums.ChatMemberStatus.OWNER:
                                creator_id = user.id
                                creator_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                            continue
                        
                        # Yönetici bilgilerini al
                        try:
                            user_full = await client.get_users(user.id)
                            about = user_full.about if hasattr(user_full, 'about') else ""
                        except:
                            about = ""
                        
                        # Kim ekledi?
                        promoted_by_id = member.promoted_by.id if member.promoted_by else None
                        promoted_by_name = f"{member.promoted_by.first_name or ''} {member.promoted_by.last_name or ''}".strip() if member.promoted_by else None
                        
                        async with db.pool.acquire() as conn:
                            await conn.execute('''
                                INSERT INTO grup_yoneticiler (
                                    grup_id, grup_name, grup_kadi, tur, rol,
                                    yonetici_id, yonetici_adsoyad, yonetici_kadi,
                                    yonetici_aciklama, kurucu_id, kurucu_adsoyad,
                                    kurucu_kadi, ekleyen_id, ekleyen_adsoyad,
                                    is_premium, is_bot, is_deleted, is_aktif_yonetici,
                                    yonetici_atama_tarih, guncel_tarih
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                                ON CONFLICT (grup_id, yonetici_id) DO UPDATE SET
                                    grup_name = $2,
                                    yonetici_adsoyad = $7,
                                    yonetici_aciklama = $9,
                                    is_premium = $15,
                                    is_aktif_yonetici = $18,
                                    guncel_tarih = $20
                            ''', chat.id, chat.title, chat.username,
                                "Süper Grup" if chat.type == types.enums.ChatType.SUPERGROUP else "Grup",
                                "Yönetici",
                                user.id,
                                f"{user.first_name or ''} {user.last_name or ''}".strip(),
                                user.username,
                                about,
                                creator_id, creator_name, None,
                                promoted_by_id, promoted_by_name,
                                user.is_premium or False,
                                False,
                                False,
                                True,
                                None,
                                datetime.now())
                        
                        total_saved += 1
                    
                    print(Fore.GREEN + f"  ✓ {chat.title} yöneticileri kaydedildi")
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
    
    return total_saved

async def collect_group_bots(clients, db, stop_scanning):
    """Grup botlarını topla"""
    print(Fore.GREEN + "\n=== GRUP BOTLARINI TOPLAMA ===\n")
    
    total_saved = 0
    
    for telegram_id, client in clients.items():
        try:
            print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için botlar taranıyor...")
            
            async for dialog in client.get_dialogs():
                if stop_scanning:
                    return total_saved
                
                chat = dialog.chat
                
                if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                    continue
                
                try:
                    async for member in client.get_chat_members(chat.id):
                        user = member.user
                        
                        if not user.is_bot:
                            continue
                        
                        # Bot bilgilerini al
                        try:
                            user_full = await client.get_users(user.id)
                            about = user_full.about if hasattr(user_full, 'about') else ""
                        except:
                            about = ""
                        
                        # Kim ekledi?
                        added_by_id = None
                        added_by_name = None
                        
                        is_admin = member.status in [types.enums.ChatMemberStatus.ADMINISTRATOR, types.enums.ChatMemberStatus.OWNER]
                        
                        async with db.pool.acquire() as conn:
                            await conn.execute('''
                                INSERT INTO grup_botlar (
                                    grup_id, grup_name, grup_kadi, tur, rol,
                                    bot_id, bot_adsoyad, bot_kadi, bot_about,
                                    ekleyen_id, ekleyen_adsoyad,
                                    is_yonetici, is_bot, is_deleted, guncel_tarih
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                                ON CONFLICT (grup_id, bot_id) DO UPDATE SET
                                    grup_name = $2,
                                    bot_adsoyad = $7,
                                    bot_about = $9,
                                    is_yonetici = $12,
                                    guncel_tarih = $15
                            ''', chat.id, chat.title, chat.username,
                                "Süper Grup" if chat.type == types.enums.ChatType.SUPERGROUP else "Grup",
                                "Yönetici" if is_admin else "Üye",
                                user.id,
                                f"{user.first_name or ''} {user.last_name or ''}".strip(),
                                user.username,
                                about,
                                added_by_id, added_by_name,
                                is_admin,
                                True,
                                False,
                                datetime.now())
                        
                        total_saved += 1
                    
                    print(Fore.GREEN + f"  ✓ {chat.title} botları kaydedildi")
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
    
    return total_saved

async def collect_group_members(clients, db, stop_scanning):
    """Grup üyelerini topla"""
    print(Fore.GREEN + "\n=== GRUP ÜYELERİNİ TOPLAMA ===\n")
    
    total_saved = 0
    
    for telegram_id, client in clients.items():
        try:
            print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için üyeler taranıyor...")
            
            async for dialog in client.get_dialogs():
                if stop_scanning:
                    return total_saved
                
                chat = dialog.chat
                
                if chat.type not in [types.enums.ChatType.GROUP, types.enums.ChatType.SUPERGROUP]:
                    continue
                
                try:
                    # Önce üye listesinden
                    async for member in client.get_chat_members(chat.id):
                        user = member.user
                        
                        # Kurucu, yönetici ve bot değilse
                        if member.status in [types.enums.ChatMemberStatus.OWNER, types.enums.ChatMemberStatus.ADMINISTRATOR] or user.is_bot:
                            continue
                        
                        try:
                            user_full = await client.get_users(user.id)
                            about = user_full.about if hasattr(user_full, 'about') else ""
                            phone = user_full.phone_number if hasattr(user_full, 'phone_number') else ""
                        except:
                            about = ""
                            phone = ""
                        
                        async with db.pool.acquire() as conn:
                            await conn.execute('''
                                INSERT INTO grup_uyeler (
                                    grup_id, grup_name, grup_kadi, tur,
                                    uye_id, uye_adsoyad, uye_kadi, uye_aciklama,
                                    uye_telefon, is_premium, is_kurucu, is_yonetici,
                                    is_bot, is_deleted, is_aktif_uye, guncel_tarih
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                                ON CONFLICT (grup_id, uye_id) DO UPDATE SET
                                    grup_name = $2,
                                    uye_adsoyad = $6,
                                    uye_aciklama = $8,
                                    is_premium = $10,
                                    is_aktif_uye = $15,
                                    guncel_tarih = $16
                            ''', chat.id, chat.title, chat.username,
                                "Süper Grup" if chat.type == types.enums.ChatType.SUPERGROUP else "Grup",
                                user.id,
                                f"{user.first_name or ''} {user.last_name or ''}".strip(),
                                user.username,
                                about,
                                phone,
                                user.is_premium or False,
                                False, False, False, False, True,
                                datetime.now())
                        
                        total_saved += 1
                    
                    print(Fore.GREEN + f"  ✓ {chat.title} üyeleri kaydedildi")
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
    
    return total_saved

async def collect_channels(clients, db, stop_scanning):
    """Kanalları topla"""
    print(Fore.GREEN + "\n=== KANALLARI TOPLAMA ===\n")
    
    total_saved = 0
    
    for telegram_id, client in clients.items():
        try:
            print(Fore.YELLOW + f"\n✓ {telegram_id} hesabı için kanallar taranıyor...")
            
            async for dialog in client.get_dialogs():
                if stop_scanning:
                    return total_saved
                
                chat = dialog.chat
                
                if chat.type != types.enums.ChatType.CHANNEL:
                    continue
                
                try:
                    chat_full = await client.get_chat(chat.id)
                    
                    # İlk mesajdan oluşturulma tarihini bul
                    creation_date = None
                    try:
                        async for message in client.get_chat_history(chat.id, limit=1, offset=-1):
                            creation_date = message.date
                    except:
                        pass
                    
                    # Link
                    if chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        try:
                            link = await client.export_chat_invite_link(chat.id)
                        except:
                            link = "Link alınamadı"
                    
                    async with db.pool.acquire() as conn:
                        await conn.execute('''
                            INSERT INTO kanallar (
                                kanal_id, kanal_name, kanal_kadi, kanal_link,
                                tur, kanal_aciklama, toplam_gorunen_uye,
                                is_kanal_gizli, is_deleted, is_kurucu,
                                kanal_kurulus_tarih, guncel_tarih
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                            ON CONFLICT (kanal_id) DO UPDATE SET
                                kanal_name = $2,
                                kanal_kadi = $3,
                                kanal_link = $4,
                                kanal_aciklama = $6,
                                toplam_gorunen_uye = $7,
                                guncel_tarih = $12
                        ''', chat.id, chat.title, chat.username, link,
                            "Kanal",
                            chat_full.description or "",
                            chat.members_count or 0,
                            chat.username is None,
                            False, True,
                            creation_date,
                            datetime.now())
                    
                    total_saved += 1
                    print(Fore.GREEN + f"  ✓ {chat.title} kaydedildi")
                    await asyncio.sleep(0.5)
                    
                except FloodWait as e:
                    print(Fore.YELLOW + f"  ⏳ FloodWait: {e.value} saniye...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    continue
        
        except Exception as e:
            continue
    
    return total_saved
