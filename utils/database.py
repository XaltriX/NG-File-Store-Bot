import time
import motor.motor_asyncio
import string
import secrets
from config import Config
from utils.helpers import ist_date, ist_midnight, trial_info

class Database:
    def __init__(self):
        pool_settings = {
            "maxPoolSize": 50,
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 20000,
            "retryWrites": True,
            "retryReads": True
        }
        
        self.client1 = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI_1, **pool_settings)
        self.db1 = self.client1[Config.MONGO_DB_NAME]
        self.files_col1 = self.db1.files
        self.users_col = self.db1.users
        self.admins_col = self.db1.admins
        self.settings_col = self.db1.settings
        self.join_reqs_col = self.db1.join_requests
        self.links_col = self.db1.invite_links 
        self.banned_col = self.db1.banned_users
        self.tokens_col = self.db1.verify_tokens
        self.verified_col = self.db1.verified_users
        self.premium_col = self.db1.premium_users
        self.vlog_col = self.db1.verify_logs
        self.stats_col = self.db1.daily_stats
        self.pay_col = self.db1.payments
        self.sync_out = self.db1.sync_outbox

        self.files_col2 = None
        if Config.MONGO_URI_2:
            self.db2 = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI_2, **pool_settings)[Config.MONGO_DB_NAME]
            self.files_col2 = self.db2.files
            
        self.files_col3 = None
        if Config.MONGO_URI_3:
            self.db3 = motor.motor_asyncio.AsyncIOMotorClient(Config.MONGO_URI_3, **pool_settings)[Config.MONGO_DB_NAME]
            self.files_col3 = self.db3.files
            
        self._is_indexed = False 
        self._cleaned_on = ''
        
        # 🚀 FIX: In-memory cache for settings to prevent DB overload
        self._settings_cache = None
        self._settings_cache_time = 0

    async def get_db_stats(self):
        stats = {}
        try:
            db1_stats = await self.db1.command("dbstats")
            stats['db1'] = {'dataSize': db1_stats.get('dataSize', 0)}
        except Exception: pass
        
        if self.files_col2:
            try:
                db2_stats = await self.db2.command("dbstats")
                stats['db2'] = {'dataSize': db2_stats.get('dataSize', 0)}
            except Exception: pass
            
        if self.files_col3:
            try:
                db3_stats = await self.db3.command("dbstats")
                stats['db3'] = {'dataSize': db3_stats.get('dataSize', 0)}
            except Exception: pass
            
        return stats

    async def delete_file(self, unique_id: str):
        res1 = await self.files_col1.delete_one({'_id': unique_id})
        if res1.deleted_count > 0: return True
        
        if self.files_col2:
            res2 = await self.files_col2.delete_one({'_id': unique_id})
            if res2.deleted_count > 0: return True
            
        if self.files_col3:
            res3 = await self.files_col3.delete_one({'_id': unique_id})
            if res3.deleted_count > 0: return True
            
        return False

    async def add_premium(self, user_id: int, time_seconds: int, daily_limit: int = 0):
        expire_at = int(time.time()) + time_seconds
        await self.premium_col.update_one(
            {'_id': user_id}, 
            {'$set': {'expire_at': expire_at, 'daily_limit': daily_limit, 'used_today': 0, 'last_date': '', 'n3': False, 'n1': False}}, 
            upsert=True
        )
        await self.mark_ever(user_id, 'ever_premium')
        
    async def remove_premium(self, user_id: int):
        await self.premium_col.delete_one({'_id': user_id})

    async def is_premium(self, user_id: int):
        doc = await self.premium_col.find_one({'_id': user_id})
        if doc and doc.get('expire_at', 0) > int(time.time()):
            return True
        if doc and doc.get('expire_at', 0) <= int(time.time()):
            await self.remove_premium(user_id) 
        return False

    async def check_and_use_premium(self, user_id: int):
        doc = await self.premium_col.find_one({'_id': user_id})
        if not doc:
            return False
        
        current_time = int(time.time())
        if doc.get('expire_at', 0) <= current_time:
            await self.remove_premium(user_id)
            return False
            
        daily_limit = doc.get('daily_limit', 0)
        if daily_limit == 0:
            return True
            
        today = ist_date()
        last_date = doc.get('last_date', '')
        
        if last_date != today:
            res = await self.premium_col.update_one(
                {'_id': user_id, 'last_date': {'$ne': today}},
                {'$set': {'last_date': today, 'used_today': 1}}
            )
            if res.modified_count > 0: return True
            
        res = await self.premium_col.update_one(
            {'_id': user_id, 'last_date': today, 'used_today': {'$lt': daily_limit}},
            {'$inc': {'used_today': 1}}
        )
        return res.modified_count > 0

    async def check_and_use_free_limit(self, user_id: int, limit: int):
        if limit <= 0: return False
        
        user = await self.get_user(user_id)
        if not user:
            await self.add_user(user_id)
            user = await self.get_user(user_id)
            
        today = ist_date()
        last_date = user.get('free_last_date', '')
        
        if last_date != today:
            res = await self.users_col.update_one(
                {'_id': user_id, 'free_last_date': {'$ne': today}},
                {'$set': {'free_last_date': today, 'free_used_today': 1}}
            )
            if res.modified_count > 0: return True
            
        res = await self.users_col.update_one(
            {'_id': user_id, 'free_last_date': today, 'free_used_today': {'$lt': limit}},
            {'$inc': {'free_used_today': 1}}
        )
        return res.modified_count > 0

    async def get_user(self, user_id: int):
        return await self.users_col.find_one({'_id': user_id})

    async def add_credits(self, user_id: int, amount: int):
        await self.users_col.update_one({'_id': user_id}, {'$inc': {'credits': amount}}, upsert=True)

    async def get_credits(self, user_id: int):
        user = await self.get_user(user_id)
        return user.get('credits', 0) if user else 0

    async def use_credit(self, user_id: int):
        result = await self.users_col.update_one(
            {'_id': user_id, 'credits': {'$gt': 0}}, 
            {'$inc': {'credits': -1}}
        )
        return result.modified_count > 0

    async def create_verify_token(self, user_id: int, payload: str, sl: int = 1):
        token = secrets.token_hex(6)
        await self.tokens_col.insert_one({'_id': token, 'user_id': user_id, 'payload': payload, 'sl': sl, 'createdAt': int(time.time())})
        return token

    async def get_verify_token(self, token: str):
        doc = await self.tokens_col.find_one_and_delete({'_id': token})
        return doc

    async def verify_user(self, user_id: int, expire_time: int):
        await self.verified_col.update_one({'_id': user_id}, {'$set': {'expire_at': expire_time}}, upsert=True)

    async def is_user_verified(self, user_id: int, current_time: int):
        doc = await self.verified_col.find_one({'_id': user_id})
        if doc and doc.get('expire_at', 0) > current_time:
            return True
        return False

    async def total_users(self):
        return await self.users_col.count_documents({})
        
    async def total_files(self):
        pipeline = [
            {
                "$project": {
                    "file_count": {
                        "$cond": {
                            "if": { "$eq": ["$t", "b"] },
                            "then": {
                                "$cond": {
                                    "if": { "$isArray": "$files" },
                                    "then": { "$size": "$files" },
                                    "else": {
                                        "$cond": {
                                            "if": { "$and": [{ "$isNumber": "$l_id" }, { "$isNumber": "$f_id" }] },
                                            "then": { "$add": [{ "$subtract": ["$l_id", "$f_id"] }, 1] },
                                            "else": 1
                                        }
                                    }
                                }
                            },
                            "else": 1
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": { "$sum": "$file_count" }
                }
            }
        ]
        
        total_count = 0
        
        async def get_collection_count(col):
            try:
                cursor = col.aggregate(pipeline)
                async for doc in cursor:
                    return doc.get("total", 0)
            except Exception:
                return await col.count_documents({})
            return 0

        total_count += await get_collection_count(self.files_col1)
        if self.files_col2: 
            total_count += await get_collection_count(self.files_col2)
        if self.files_col3: 
            total_count += await get_collection_count(self.files_col3)
            
        return total_count
        
    async def total_banned_users(self):
        return await self.banned_col.count_documents({})
        
    async def get_all_users(self):
        return self.users_col.find({})
        
    async def ban_user(self, user_id: int):
        await self.banned_col.update_one({'_id': user_id}, {'$set': {'banned': True}}, upsert=True)
        
    async def unban_user(self, user_id: int):
        await self.banned_col.delete_one({'_id': user_id})
        
    async def unban_all_users(self):
        result = await self.banned_col.delete_many({})
        return result.deleted_count
        
    async def is_banned(self, user_id: int):
        return bool(await self.banned_col.find_one({'_id': user_id}))

    async def save_invite_link(self, chat_id: int, link: str, expire_at: int):
        await self.links_col.insert_one({'chat_id': chat_id, 'link': link, 'expire_at': expire_at})

    async def get_expired_links(self, current_time: int):
        cursor = self.links_col.find({'expire_at': {'$lte': current_time}})
        return await cursor.to_list(length=None)

    async def remove_invite_link(self, link: str):
        await self.links_col.delete_one({'link': link})

    async def add_join_request(self, user_id: int, chat_id: int):
        await self.join_reqs_col.update_one({'user_id': user_id, 'chat_id': chat_id}, {'$set': {'requested': True}}, upsert=True)

    async def has_join_request(self, user_id: int, chat_id: int):
        return bool(await self.join_reqs_col.find_one({'user_id': user_id, 'chat_id': chat_id}))

    async def get_fsub_channels(self):
        settings = await self.get_settings()
        return settings.get('fsub_channels', []) if settings else []

    async def add_fsub_channel(self, chat_id: int):
        await self.settings_col.update_one({'_id': 'bot_settings'}, {'$addToSet': {'fsub_channels': chat_id}}, upsert=True)
        self._settings_cache = None # 🚀 FIX: Invalidate cache

    async def remove_fsub_channel(self, chat_id: int):
        await self.settings_col.update_one({'_id': 'bot_settings'}, {'$pull': {'fsub_channels': chat_id}}, upsert=True)
        self._settings_cache = None # 🚀 FIX: Invalidate cache

    async def add_admin(self, user_id: int):
        if not await self.admins_col.find_one({'_id': user_id}):
            await self.admins_col.insert_one({'_id': user_id})
            return True
        return False

    async def remove_admin(self, user_id: int):
        await self.admins_col.delete_one({'_id': user_id})

    async def is_admin(self, user_id: int):
        if user_id == Config.OWNER_ID:
            return True
        return bool(await self.admins_col.find_one({'_id': user_id}))

    async def add_user(self, user_id: int):
        if not await self.users_col.find_one({'_id': user_id}):
            await self.users_col.insert_one({'_id': user_id})
            return True 
        return False

    async def get_settings(self):
        # 🚀 FIX: Smart In-Memory Cache (60 seconds TTL)
        current_time = time.time()
        if self._settings_cache and (current_time - self._settings_cache_time) < 60:
            return self._settings_cache

        settings = await self.settings_col.find_one({'_id': 'bot_settings'})
        default_db = Config.DB_CHANNEL if Config.DB_CHANNEL != 0 else None
        default_log = Config.LOG_CHANNEL if Config.LOG_CHANNEL != 0 else None
        
        default_settings = {
            'active_db': default_db,
            'log_channel': default_log,
            'mode': 'public',
            'req_fsub': False,
            'auto_delete': 0,
            'shortlink_status': False,
            'shortlink_type': 'time',
            'verify_duration': 24,
            'bypass_credits': 3,
            'shortener_url': Config.SHORTENER_URL,
            'shortener_api': Config.SHORTENER_API,
            'tutorial_link': Config.TUTORIAL_LINK,
            'protect_content': False,
            'owner_link': '',
            'group_link': '',
            'free_daily_limit': 3,
            'premium_plans': self._default_plans(),
            'dual_shortner': False,
            'share_button': True,
            'proof_enabled': True, 'proof_chat': 0, 'proof_caption': '',
            'shortener2_url': '', 'shortener2_api': '', 'tutorial2_link': '',
            'trial_enabled': True, 'trial_days': 3, 'trial_daily': 5,
            'reminder_enabled': True, 'reminder_hours': 12, 'quiet_hours': True,
            'upi_id': 'kunaljaisinghpur@axl', 'owner_handle': '@NeonGhost',
            'qr_url': 'https://files.catbox.moe/2qdo4w.png',
            'info_link': 'https://t.me/NgPremiumX/9',
            'preview_link': 'https://t.me/+xlTrZ9h4Ngg2Yjg8',
            'proofs_link': 'https://t.me/+YKC50zCkuqU0ZjM0',
            'qr_link': 'https://t.me/NgPremiumX/13',
            'card_custom_en': '', 'card_custom_hi': '',
            'sync_enabled': False, 'sync_url': '', 'sync_db': 'sync_mailbox', 'partner_username': '',
            'sync_last_ok': 0, 'sync_err': '',
            'payment_info': 'Sᴇɴᴅ ᴍᴏɴᴇʏ ᴛᴏ Bᴋᴀsʜ/Nᴀɢᴀᴅ ᴀɴᴅ ᴄᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ ᴡɪᴛʜ Sᴄʀᴇᴇɴsʜᴏᴛ.'
        }
        
        if settings:
            for key, value in default_settings.items():
                if key not in settings or settings[key] is None:
                    settings[key] = value
            
            if not isinstance(settings.get('premium_plans'), list):
                settings['premium_plans'] = self._default_plans()
            if not settings.get('active_db') and default_db:
                settings['active_db'] = default_db
            if not settings.get('log_channel') and default_log:
                settings['log_channel'] = default_log
                
            self._settings_cache = settings
            self._settings_cache_time = current_time
            return settings
            
        self._settings_cache = default_settings
        self._settings_cache_time = current_time
        return default_settings

    async def update_settings(self, key: str, value):
        await self.settings_col.update_one({'_id': 'bot_settings'}, {'$set': {key: value}}, upsert=True)
        self._settings_cache = None # 🚀 FIX: Invalidate cache

    async def generate_unique_id(self, length=50):
        # 🚀 FIX: Removed the infinite loop and DB check. Ultra-fast generation!
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    async def _insert_doc(self, doc):
        try:
            await self.files_col1.insert_one(doc)
            return True 
        except Exception:
            if self.files_col2:
                try:
                    await self.files_col2.insert_one(doc)
                    return True 
                except Exception:
                    pass
            if self.files_col3:
                try:
                    await self.files_col3.insert_one(doc)
                    return True 
                except Exception:
                    pass
        raise Exception("Database Save Failed") 
        
    # 🚀 FIX: Multi-DB Auto-heal Support
    async def update_file_data(self, unique_id: str, update_data: dict):
        res1 = await self.files_col1.update_one({'_id': unique_id}, {'$set': update_data})
        if res1.modified_count > 0: return True
        
        if self.files_col2:
            res2 = await self.files_col2.update_one({'_id': unique_id}, {'$set': update_data})
            if res2.modified_count > 0: return True
            
        if self.files_col3:
            res3 = await self.files_col3.update_one({'_id': unique_id}, {'$set': update_data})
            if res3.modified_count > 0: return True
            
        return False

    async def save_file(self, message_id: int, chat_id: int, file_id: str, file_unique_id: str, caption: str = ""):
        unique_id = await self.generate_unique_id()
        doc = {'_id': unique_id, 't': 's', 'm': message_id, 'c': chat_id}
        if file_id: doc['f'] = file_id
        if file_unique_id: doc['u'] = file_unique_id
        if caption: doc['cap'] = caption
        try:
            await self._insert_doc(doc)
            return unique_id
        except Exception:
            return None 

    async def save_batch(self, first_id: int = 0, last_id: int = 0, chat_id: int = 0, files_data: list = None):
        unique_id = await self.generate_unique_id()
        if files_data:
            doc = {'_id': unique_id, 't': 'b', 'files': files_data, 'c': chat_id} 
        else:
            doc = {'_id': unique_id, 't': 'b', 'f_id': first_id, 'l_id': last_id, 'c': chat_id}
        try:
            await self._insert_doc(doc)
            return unique_id
        except Exception:
            return None

    async def check_file_exists(self, file_unique_id: str):
        if not file_unique_id: return None
        
        if not self._is_indexed:
            try:
                await self.files_col1.create_index([("u", 1)], background=True, sparse=True)
                if self.files_col2: await self.files_col2.create_index([("u", 1)], background=True, sparse=True)
                if self.files_col3: await self.files_col3.create_index([("u", 1)], background=True, sparse=True)
            except Exception: pass
            self._is_indexed = True

        projection = {'_id': 1}
        doc = await self.files_col1.find_one({'u': file_unique_id}, projection)
        if not doc and self.files_col2: doc = await self.files_col2.find_one({'u': file_unique_id}, projection)
        if not doc and self.files_col3: doc = await self.files_col3.find_one({'u': file_unique_id}, projection)
        return doc

    async def get_file(self, unique_id: str):
        projection = {'_id': 1, 't': 1, 'm': 1, 'c': 1, 'f': 1, 'u': 1, 'cap': 1, 'f_id': 1, 'l_id': 1, 'files': 1}
        doc = await self.files_col1.find_one({'_id': unique_id}, projection)
        if not doc and self.files_col2: doc = await self.files_col2.find_one({'_id': unique_id}, projection)
        if not doc and self.files_col3: doc = await self.files_col3.find_one({'_id': unique_id}, projection)
        return doc

    # ================= Defaults =================
    @staticmethod
    def _default_plans():
        return [
            {'id': 'p1', 'name': '1 Month', 'name_hi': '1 महीना', 'price': 99, 'days': 30},
            {'id': 'p2', 'name': '3 Months', 'name_hi': '3 महीने', 'price': 199, 'days': 90},
            {'id': 'p3', 'name': '6 Months', 'name_hi': '6 महीने', 'price': 299, 'days': 180},
            {'id': 'p4', 'name': '1 Year', 'name_hi': '1 साल', 'price': 399, 'days': 365},
        ]

    # ================= Language =================
    async def set_lang(self, user_id: int, lang: str):
        await self.users_col.update_one({'_id': user_id}, {'$set': {'lang': lang}}, upsert=True)

    # ================= Daily stats (IST, today + yesterday only) =================
    async def _cleanup_daily(self, today: str):
        if self._cleaned_on == today:
            return
        self._cleaned_on = today
        cutoff = ist_date(1)
        try:
            await self.vlog_col.delete_many({'date': {'$lt': cutoff}})
            await self.stats_col.delete_many({'_id': {'$lt': cutoff}})
        except Exception:
            pass

    async def bump_stat(self, key: str, n: int = 1):
        today = ist_date()
        await self._cleanup_daily(today)
        await self.stats_col.update_one({'_id': today}, {'$inc': {key: n}}, upsert=True)

    async def get_day_stats(self, offset: int = 0):
        return await self.stats_col.find_one({'_id': ist_date(offset)}) or {}

    async def log_verify(self, user_id: int, sl: int = 1):
        today = ist_date()
        await self._cleanup_daily(today)
        await self.mark_ever(user_id, 'ever_verified')
        await self.vlog_col.update_one(
            {'_id': f"{today}_{user_id}_{sl}"},
            {'$setOnInsert': {'date': today, 'u': user_id, 's': sl}},
            upsert=True
        )

    async def verify_counts(self):
        await self._cleanup_daily(ist_date())
        out = {}
        for name, off in (('today', 0), ('yesterday', 1)):
            d = ist_date(off)
            users = await self.vlog_col.distinct('u', {'date': d})
            per = {}
            for n in self.SL_KEYS:
                per[n] = await self.vlog_col.count_documents({'date': d, 's': n})
            out[name] = {'total': len(users), 's': per}
        return out

    # ================= Dual shortner (add a 3rd by extending SL_KEYS) =================
    SL_KEYS = {
        1: ('shortener_url', 'shortener_api', 'tutorial_link'),
        2: ('shortener2_url', 'shortener2_api', 'tutorial2_link'),
    }

    def sl_config(self, settings: dict, n: int):
        ku, ka, kt = self.SL_KEYS[n]
        return (settings.get(ku) or '', settings.get(ka) or '', settings.get(kt) or '')

    async def pick_shortner(self, user_id: int, settings: dict) -> int:
        ready = [n for n in self.SL_KEYS if all(self.sl_config(settings, n)[:2])]
        if not ready:
            return 1
        if not settings.get('dual_shortner', False) or len(ready) < 2:
            return ready[0]
        user = await self.get_user(user_id)
        last = (user or {}).get('last_sl', 0)
        after = [n for n in ready if n > last]
        return after[0] if after else ready[0]

    async def set_last_sl(self, user_id: int, n: int):
        await self.users_col.update_one({'_id': user_id}, {'$set': {'last_sl': n}}, upsert=True)

    # ================= Trial =================
    async def use_trial(self, user_id: int, settings: dict):
        """Consume one trial link. Returns (info or None, phase)."""
        user = await self.get_user(user_id)
        if not user:
            await self.add_user(user_id)
            user = await self.get_user(user_id) or {}
        info = trial_info(user, settings)
        phase = info['phase']
        if phase in ('off', 'ended'):
            return None, phase
        if phase == 'new':
            res = await self.users_col.update_one(
                {'_id': user_id, 'trial_start': {'$exists': False}},
                {'$set': {'trial_start': int(time.time())}}
            )
            if res.modified_count:
                await self.bump_stat('trials_started')
            user = await self.get_user(user_id) or {}
            info = trial_info(user, settings)
            if info['phase'] != 'active':
                return None, info['phase']
        daily = info['daily']
        today = ist_date()
        res = await self.users_col.update_one(
            {'_id': user_id, 'trial_date': {'$ne': today}},
            {'$set': {'trial_date': today, 'trial_used': 1}}
        )
        if res.modified_count:
            used = 1
        else:
            res = await self.users_col.update_one(
                {'_id': user_id, 'trial_date': today, 'trial_used': {'$lt': daily}},
                {'$inc': {'trial_used': 1}}
            )
            if not res.modified_count:
                return None, 'active'
            used = info.get('used', 0) + 1
        return {'day': info['day'], 'days': info['days'], 'daily': daily,
                'used': used, 'left': max(daily - used, 0)}, 'active'

    # ================= Access helpers =================
    async def premium_expire(self, user_id: int):
        doc = await self.premium_col.find_one({'_id': user_id})
        if doc and doc.get('expire_at', 0) > int(time.time()):
            return doc['expire_at']
        return 0

    async def verified_expire(self, user_id: int):
        doc = await self.verified_col.find_one({'_id': user_id})
        if doc and doc.get('expire_at', 0) > int(time.time()):
            return doc['expire_at']
        return 0

    async def extend_premium(self, user_id: int, days: int):
        now = int(time.time())
        doc = await self.premium_col.find_one({'_id': user_id})
        base = doc['expire_at'] if doc and doc.get('expire_at', 0) > now else now
        expire_at = base + days * 86400
        await self.premium_col.update_one(
            {'_id': user_id},
            {'$set': {'expire_at': expire_at, 'daily_limit': 0, 'used_today': 0, 'last_date': '', 'n3': False, 'n1': False}},
            upsert=True
        )
        await self.mark_ever(user_id, 'ever_premium')
        return expire_at

    # ================= Reminders =================
    async def reminder_candidates(self, settings: dict, limit: int = 100):
        days = int(settings.get('trial_days', 3) or 1)
        hours = int(settings.get('reminder_hours', 12) or 12)
        now = int(time.time())
        cutoff = ist_midnight(-(days - 1))
        query = {
            'trial_start': {'$lt': cutoff},
            'reminder_off': {'$ne': True},
            '$and': [
                {'$or': [{'last_rem': {'$exists': False}}, {'last_rem': {'$lte': now - hours * 3600}}]},
                {'$or': [{'rem_ignored': {'$exists': False}}, {'rem_ignored': {'$lt': 5}}]},
            ],
        }
        return await self.users_col.find(query).limit(limit).to_list(length=limit)

    async def mark_checked(self, user_id: int):
        await self.users_col.update_one({'_id': user_id}, {'$set': {'last_rem': int(time.time())}})

    async def mark_reminded(self, user_id: int, msg_id: int):
        await self.users_col.update_one(
            {'_id': user_id},
            {'$set': {'last_rem': int(time.time()), 'rem_msg': msg_id}, '$inc': {'rem_ignored': 1}}
        )

    async def mark_reminder_off(self, user_id: int):
        await self.users_col.update_one({'_id': user_id}, {'$set': {'reminder_off': True}})

    async def reset_ignored(self, user_id: int):
        await self.users_col.update_one({'_id': user_id, 'rem_ignored': {'$gt': 0}}, {'$set': {'rem_ignored': 0}})

    async def premium_expiring(self):
        now = int(time.time())
        cur = self.premium_col.find({'expire_at': {'$gt': now, '$lte': now + 3 * 86400}})
        return await cur.to_list(length=500)

    async def mark_prem_notified(self, user_id: int, flags: list):
        await self.premium_col.update_one({'_id': user_id}, {'$set': {f: True for f in flags}})

    # ================= Payments =================
    async def create_payment(self, user_id: int, plan: dict, extra: dict = None):
        pid = secrets.token_hex(4)
        doc = {
            '_id': pid, 'u': user_id, 'plan': plan['id'], 'price': plan['price'],
            'days': plan['days'], 'status': 'pending', 'ts': int(time.time()), 'date': ist_date()
        }
        if extra:
            doc.update(extra)
        await self.pay_col.insert_one(doc)
        return pid

    async def get_payment(self, pid: str):
        return await self.pay_col.find_one({'_id': pid})

    async def set_payment_post(self, pid: str, flag: bool):
        await self.pay_col.update_one({'_id': pid, 'status': 'pending'}, {'$set': {'post_proof': bool(flag)}})

    async def pending_payment(self, user_id: int, within: int = 1800):
        return await self.pay_col.find_one(
            {'u': user_id, 'status': 'pending', 'ts': {'$gt': int(time.time()) - within}}
        )

    async def claim_payment(self, pid: str, status: str, by: int, plan_id: str = None):
        upd = {'status': status, 'by': by, 'done': int(time.time())}
        if plan_id:
            upd['final_plan'] = plan_id
        return await self.pay_col.find_one_and_update({'_id': pid, 'status': 'pending'}, {'$set': upd})

    async def set_pay_plan(self, user_id: int, plan_id):
        if plan_id:
            await self.users_col.update_one({'_id': user_id}, {'$set': {'pay_plan': plan_id, 'pay_ts': int(time.time())}}, upsert=True)
        else:
            await self.users_col.update_one({'_id': user_id}, {'$unset': {'pay_plan': ''}})


    # ================= Lifetime flags (never deleted) =================
    async def mark_ever(self, user_id: int, field: str):
        await self.users_col.update_one({'_id': user_id}, {'$set': {field: True}}, upsert=True)

    async def backfill_flags(self):
        """One-time: flag everyone who is/was premium or verified (incl. old rohit_1888 'verify_status')."""
        s = await self.get_settings()
        if s.get('flags_backfilled'):
            return
        for col, field in ((self.premium_col, 'ever_premium'), (self.verified_col, 'ever_verified')):
            async for d in col.find({}, {'_id': 1}):
                await self.mark_ever(d['_id'], field)
        await self.users_col.update_many(
            {'$or': [{'verify_status.is_verified': True},
                     {'verify_status.verified_time': {'$exists': True, '$nin': ['', 0, None]}}]},
            {'$set': {'ever_verified': True}}
        )
        await self.update_settings('flags_backfilled', True)

    async def premium_stats(self):
        now = int(time.time())
        cur = await self.premium_col.count_documents({'expire_at': {'$gt': now}})
        ever = await self.users_col.count_documents({'ever_premium': True})
        return cur, max(ever, cur)

    async def verified_stats(self, credit_mode: bool = False):
        ever = await self.users_col.count_documents({'ever_verified': True})
        if credit_mode:
            cur = await self.users_col.count_documents({'credits': {'$gt': 0}})
        else:
            cur = await self.verified_col.count_documents({'expire_at': {'$gt': int(time.time())}})
        return cur, max(ever, cur)

    # ================= Premium list =================
    async def premium_counts(self):
        now = int(time.time())
        active = await self.premium_col.count_documents({'expire_at': {'$gt': now}})
        soon = await self.premium_col.count_documents({'expire_at': {'$gt': now, '$lte': now + 3 * 86400}})
        return active, soon

    async def premium_docs(self, tab: str, page: int, per: int = 8):
        now = int(time.time())
        q = {'expire_at': {'$gt': now}} if tab == 'active' else {'expire_at': {'$gt': now, '$lte': now + 3 * 86400}}
        return await self.premium_col.find(q).sort('expire_at', 1).skip(page * per).limit(per).to_list(length=per)

    # ================= Broadcast targets =================
    BC_FILTERS = {'all': {}, 'prem': {'ever_premium': True}, 'ver': {'ever_verified': True}}

    async def target_count(self, target: str):
        return await self.users_col.count_documents(self.BC_FILTERS.get(target, {}))

    # ================= Pending payments =================
    async def pending_count(self):
        return await self.pay_col.count_documents({'status': 'pending'})

    async def pending_list(self, limit: int = 6):
        return await self.pay_col.find({'status': 'pending'}).sort('ts', -1).limit(limit).to_list(length=limit)

    # ================= Partner sync outbox =================
    async def sync_queue(self, user_id: int, days: int, ref: str):
        s = await self.get_settings()
        if not (s.get('sync_enabled') and s.get('sync_url')):
            return False
        await self.sync_out.update_one(
            {'_id': ref},
            {'$setOnInsert': {'u': user_id, 'days': int(days), 'ts': int(time.time()), 'sent': False}},
            upsert=True
        )
        return True

    async def sync_unsent(self, limit: int = 50):
        return await self.sync_out.find({'sent': False}).limit(limit).to_list(length=limit)

    async def sync_mark_sent(self, ref: str):
        await self.sync_out.update_one({'_id': ref}, {'$set': {'sent': True, 'sent_at': int(time.time())}})

    async def sync_pending_count(self):
        return await self.sync_out.count_documents({'sent': False})

    async def sync_cleanup(self, before_ts: int):
        await self.sync_out.delete_many({'sent': True, 'sent_at': {'$lt': before_ts}})


db = Database()
