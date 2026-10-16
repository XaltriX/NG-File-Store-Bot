"""All user-facing texts (English default + Devanagari Hindi)."""

PREMIUM_CARD_EN = (
    "💎 <b>Choose Your Plan</b>\n\n"
    "<blockquote>🎁 <b>One payment. Two bots.</b>\n{bots}\n"
    "<i>Pay in either bot. Premium turns on in both.</i></blockquote>\n\n{best}{proof}\n"
    "<b>How it works</b>\n1️⃣ Pick a plan → 2️⃣ Pay by UPI → 3️⃣ Send screenshot → 4️⃣ Done\n\n"
    "👇 <i>Pick a plan to continue</i>"
)

PREMIUM_CARD_HI = (
    "💎 <b>अपना प्लान चुनें</b>\n\n"
    "<blockquote>🎁 <b>एक पेमेंट। दो बॉट।</b>\n{bots}\n"
    "<i>किसी भी बॉट में पेमेंट करें। प्रीमियम दोनों में चालू होगा।</i></blockquote>\n\n{best}{proof}\n"
    "<b>कैसे होगा</b>\n1️⃣ प्लान चुनें → 2️⃣ UPI से पेमेंट → 3️⃣ स्क्रीनशॉट भेजें → 4️⃣ हो गया\n\n"
    "👇 <i>आगे बढ़ने के लिए प्लान चुनें</i>"
)

PREMIUM_SOLO_EN = (
    "💎 <b>Choose Your Plan</b>\n\n{best}{proof}\n"
    "<b>How it works</b>\n1️⃣ Pick a plan → 2️⃣ Pay by UPI → 3️⃣ Send screenshot → 4️⃣ Done\n\n"
    "👇 <i>Pick a plan to continue</i>"
)

PREMIUM_SOLO_HI = (
    "💎 <b>अपना प्लान चुनें</b>\n\n{best}{proof}\n"
    "<b>कैसे होगा</b>\n1️⃣ प्लान चुनें → 2️⃣ UPI से पेमेंट → 3️⃣ स्क्रीनशॉट भेजें → 4️⃣ हो गया\n\n"
    "👇 <i>आगे बढ़ने के लिए प्लान चुनें</i>"
)

PROOF_CAPTION = (
    "╔═ ✦ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 ✦ ═╗\n\n"
    "🎉 <b>𝗡𝗲𝘄 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗠𝗲𝗺𝗯𝗲𝗿 𝗝𝗼𝗶𝗻𝗲𝗱!</b>\n\n"
    "▌ 👤 <b>Member</b> ➜ {name}\n"
    "▌ 🪙 <b>Plan</b> ➜ {plan}\n"
    "▌ 📅 <b>Validity</b> ➜ {days} Days\n"
    "▌ 🤖 <b>Bots</b> ➜ {bots}\n\n"
    "🚫 𝗡𝗼 𝗮𝗱𝘀 · ✅ 𝗡𝗼 𝘃𝗲𝗿𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻 · ⚡ 𝗗𝗶𝗿𝗲𝗰𝘁 𝘃𝗶𝗱𝗲𝗼𝘀\n\n"
    "✨ <i>Your turn could be next. Get Premium and watch without limits!</i>"
)

REMINDER_EN = ("👋 <b>Still looking for more?</b>\n\nYour free access is one tap away. "
               "Verify in seconds, or go Premium for instant, ad-free files.")
REMINDER_HI = ("👋 <b>और फ़ाइलें चाहिए?</b>\n\nआपका फ्री एक्सेस बस एक टैप दूर है। "
               "कुछ सेकंड में वेरिफाई करें, या प्रीमियम लेकर तुरंत और बिना विज्ञापन फ़ाइलें पाएं।")

STR = {
    'en': {
        'lang_pick': "🌐 <b>Choose your language</b>\n<b>अपनी भाषा चुनें</b>",
        'welcome': (
    '✨ <b>Welcome, {name}!</b>\n\n'
    '<blockquote>'
    '📦 𝙁𝙞𝙡𝙚 → 𝙇𝙞𝙣𝙠 𝘽𝙤𝙩\n'
    '👨‍💻 𝘽𝙮 <a href="https://t.me/NeonGhost"><b>NeonGhost</b></a>\n\n'
    '⚡ <b>Works for:</b> <a href="https://t.me/Linkz_Wallah"><b>@Linkz_Wallah</b></a>\n'
    '🎬 <b>Movies:</b> <a href="https://t.me/+p2dAkUL0d2NhYTM9"><b>𝙊𝙥𝙚𝙣 𝙈𝙤𝙫𝙞𝙚𝙨</b></a>'
    '</blockquote>'
),
        'w_premium': "\n\n💎 <b>Premium active</b> · till {date}",
        'w_trial': "\n\n🎁 <b>Free trial</b> · Day {day}/{days} · {left}/{daily} links left today",
        'w_trial_new': "\n\n🎁 <b>Free trial</b> · {days} days, {daily} links a day. Starts with your first link.",
        'w_credits': "\n\n💳 <b>Credits:</b> <code>{creds}</code>",
        'b_status': '📋 My Status', 'b_premium': '💎 Premium', 'b_updates': '📢 Updates', 'b_support': '🛟 Support',
        'b_admin': '🛠 Admin Panel', 'b_back': '⬅️ Back', 'b_close': '✖️ Close', 'b_lang': '🌐 Language',
        'b_verify': '🔓 Free Verify', 'b_tutorial': '🎥 How to verify', 'b_paid': "✅ I've Paid",
        'b_change': '🔄 Change Plan', 'b_cancel': '✖️ Cancel', 'b_renew': '🔁 Renew', 'b_upgrade': '⬆️ Upgrade Plan',
        'b_contact': '🛟 Contact Support',
        'b_contact_owner': '💬 Contact Owner',
        'b_more': '🎬 More Videos',
        'b_refer': '🎁 Refer & Earn',
        'b_share_link': '📤 Share my link',
        'ref_screen': "🎁 <b>𝗥𝗘𝗙𝗘𝗥 & 𝗘𝗔𝗥𝗡</b>\n\n<blockquote>👥 Invite friends. <b>Every {need} friends = {days} day Premium</b>, instantly, in both bots.</blockquote>\n\n▌ 🔗 <b>Your referrals:</b> {count}\n▌ 🎯 <b>Next reward in:</b> {left} more  {bar}\n▌ 🏅 <b>Premium days earned:</b> {earned}\n▌ 📍 <b>Your rank this week:</b> {rank}\n\n🏆 <b>𝗧𝗢𝗣 𝟱 𝗧𝗛𝗜𝗦 𝗪𝗘𝗘𝗞</b>\n{top}\n<i>Weekly bonus Premium: {prizes}</i>\n\n🔗 <b>Your link</b> (tap to copy)\n<code>{link}</code>",
        'ref_none': 'No referrals yet this week. Be the first!',
        'ref_off': 'Refer & Earn is not available right now.',
        'ref_reward': "🎉 <b>Referral reward!</b>\n\n<blockquote>👥 <b>{total}</b> friends joined through your link.\n🎁 <b>+{days} day(s)</b> full Premium added.\n📅 Valid till: <b>{date}</b></blockquote>\n\n🔥 Every {need} friends = {days} more day(s). Keep sharing!",
        'ref_week_prize': "🏆 <b>Weekly Referral Champion!</b>\n\n<blockquote>🏅 You finished <b>#{rank}</b> last week with <b>{n}</b> active referrals.\n🎁 Prize: <b>+{days} days</b> Premium\n📅 Valid till: <b>{date}</b></blockquote>\n\n🔥 A new week just started. Keep inviting!",
        'ref_share_text': '🎁 Join this bot and watch movies & series on Telegram!',
        'b_share': '📤 Share this',
        'share_text': '🎬 Watch this on Telegram!',
        'status': '📋 <b>YOUR STATUS</b>\n\n<blockquote>💎 <b>Plan:</b> {plan}\n🎁 <b>Trial:</b> {trial}\n🔓 <b>Access:</b> {access}\n📥 <b>Free links today:</b> {free}</blockquote>',
        'st_free': "Free", 'st_prem': "Premium · till {date}",
        'st_trial_on': "Day {day}/{days} · {left}/{daily} links left today",
        'st_trial_new': "Not started yet", 'st_trial_end': "Ended", 'st_trial_off': "Not available",
        'st_acc_time': "Verified · till {time}", 'st_acc_credit': "{creds} credits", 'st_acc_none': "Not verified",
        'st_acc_open': "Open for everyone",
        'st_free_left': "{left}/{limit} left",
        'generating': "⏳ Generating your secure link...",
        'locked_trial_end': "🔒 <b>Your free trial has ended</b>",
        'locked_trial_today': "🔒 <b>Today's free trial links are used</b>",
        'locked_normal': "🔒 <b>Verification required</b>",
        'locked_body': '{head}\n\n<blockquote>🔓 <b>Free Verify</b> — {benefit}\n💎 <b>Premium</b> — instant, ad-free access</blockquote>\n\n👇 <i>Tap a button below</i>',
        'benefit_time': "free access for {hours} hours", 'benefit_credit': "{creds} file links",
        'ver_ok_time': '✅ <b>Verified!</b>\n\n<blockquote>⏳ You have access for <b>{duration} hours</b>.</blockquote>',
        'ver_ok_credit': '✅ <b>Verified!</b>\n\n<blockquote>🎁 <b>{creds}</b> file credits added.</blockquote>',
        'ver_ok_nofile': "\n\nOpen your file link again to get your files.",
        'already_active': "✅ Your access is already active. Open your file link to continue.",
        'trial_note': "🎁 Free trial · Day {day}/{days} · {left}/{daily} links left today",
        'trial_last': "🎁 That was your last trial link for today. Come back tomorrow, or choose Free Verify / Premium for more.",
        'pay_caption': "💳 <b>Selected plan:</b> {plan}\n\n<blockquote>📱 Scan the QR code or pay to this UPI ID\n<code>{upi}</code></blockquote>\n\n✅ After paying, tap <b>I've Paid</b> and send your screenshot.",
        'ask_ss': '📸 <b>Send your payment screenshot now</b>\n\n🪙 Plan: {plan}',
        'ss_got': "✅ <b>Screenshot received!</b>\n\n⏳ Your payment is under review. You'll get a message here as soon as it's approved.",
        'ss_pending': "⏳ Your payment is already under review. Please wait a little.",
        'ss_bad': "Please send a photo (screenshot) of your payment.",
        'approved': '🎉 <b>Premium activated!</b>\n\n<blockquote>🪙 <b>Plan:</b> {plan}\n📅 <b>Valid till:</b> {date}</blockquote>\n\n⚡ Enjoy instant, ad-free access.',
        'approved_diff': "🎉 <b>Premium activated!</b>\n\nYou selected {sel}, but your payment matched <b>{plan}</b>, so that plan is active.\nValid till: <b>{date}</b>\n\nWant a longer plan? Tap Upgrade Plan.",
        'rejected': "❌ We couldn't verify your payment.\n\nIf you have paid, please contact support with your screenshot.",
        'exp_soon': '⏰ <b>Premium expiring soon</b>\n\n<blockquote>Your Premium ends in <b>{days} day(s)</b>, on {date}.</blockquote>\n\n🔁 Renew now to keep instant, ad-free access.',
        'prem_gone': "Premium is not available right now.",
    },
    'hi': {
        'lang_pick': "🌐 <b>Choose your language</b>\n<b>अपनी भाषा चुनें</b>",
        'welcome': (
    '✨ <b>स्वागत है, {name}!</b>\n\n'
    '<blockquote>'
    '📦 𝙁𝙞𝙡𝙚 → 𝙇𝙞𝙣𝙠 𝘽𝙤𝙩\n'
    '👨‍💻 𝘽𝙮 <a href="https://t.me/NeonGhost"><b>NeonGhost</b></a>\n\n'
    '⚡ <b>यह काम करता है:</b> <a href="https://t.me/Linkz_Wallah"><b>@Linkz_Wallah</b></a> के लिए\n'
    '🎬 <b>Movies:</b> <a href="https://t.me/+p2dAkUL0d2NhYTM9"><b>𝙈𝙤𝙫𝙞𝙚𝙨 𝙊𝙥𝙚𝙣 𝙆𝙖𝙧𝙚𝙣</b></a>'
    '</blockquote>'
),
        'w_premium': "\n\n💎 <b>प्रीमियम एक्टिव</b> · {date} तक",
        'w_trial': "\n\n🎁 <b>फ्री ट्रायल</b> · दिन {day}/{days} · आज {left}/{daily} लिंक बाकी",
        'w_trial_new': "\n\n🎁 <b>फ्री ट्रायल</b> · {days} दिन, रोज़ {daily} लिंक। पहले लिंक से शुरू।",
        'w_credits': "\n\n💳 <b>क्रेडिट:</b> <code>{creds}</code>",
        'b_status': '📋 मेरी स्थिति', 'b_premium': '💎 प्रीमियम', 'b_updates': '📢 अपडेट्स', 'b_support': '🛟 सपोर्ट',
        'b_admin': '🛠 Admin Panel', 'b_back': '⬅️ वापस', 'b_close': '✖️ बंद करें', 'b_lang': '🌐 भाषा',
        'b_verify': '🔓 फ्री वेरिफाई', 'b_tutorial': '🎥 वेरिफाई कैसे करें', 'b_paid': '✅ मैंने पेमेंट कर दिया',
        'b_change': '🔄 प्लान बदलें', 'b_cancel': '✖️ रद्द करें', 'b_renew': '🔁 रिन्यू करें', 'b_upgrade': '⬆️ प्लान अपग्रेड करें',
        'b_contact': '🛟 सपोर्ट से संपर्क करें',
        'b_contact_owner': '💬 ओनर से संपर्क करें',
        'b_more': '🎬 और वीडियो',
        'b_refer': '🎁 रेफर करें और कमाएं',
        'b_share_link': '📤 मेरा लिंक शेयर करें',
        'ref_screen': "🎁 <b>𝗥𝗘𝗙𝗘𝗥 & 𝗘𝗔𝗥𝗡</b>\n\n<blockquote>👥 दोस्तों को बुलाएं। <b>हर {need} दोस्त = {days} दिन प्रीमियम</b>, तुरंत, दोनों बॉट में।</blockquote>\n\n▌ 🔗 <b>आपके रेफरल:</b> {count}\n▌ 🎯 <b>अगला इनाम:</b> {left} और  {bar}\n▌ 🏅 <b>कमाए प्रीमियम दिन:</b> {earned}\n▌ 📍 <b>इस हफ्ते आपकी रैंक:</b> {rank}\n\n🏆 <b>𝗜𝗦 𝗛𝗔𝗙𝗧𝗘 𝗞𝗔 𝗧𝗢𝗣 𝟱</b>\n{top}\n<i>साप्ताहिक बोनस प्रीमियम: {prizes}</i>\n\n🔗 <b>आपका लिंक</b> (कॉपी करने के लिए टैप करें)\n<code>{link}</code>",
        'ref_none': 'इस हफ्ते अभी कोई रेफरल नहीं। पहले आप बनें!',
        'ref_off': 'रेफर और कमाएं अभी उपलब्ध नहीं है।',
        'ref_reward': "🎉 <b>रेफरल इनाम!</b>\n\n<blockquote>👥 आपके लिंक से <b>{total}</b> दोस्त जुड़ चुके हैं।\n🎁 <b>+{days} दिन</b> फुल प्रीमियम जुड़ गया।\n📅 वैधता: <b>{date}</b> तक</blockquote>\n\n🔥 हर {need} दोस्त पर {days} दिन और। शेयर करते रहें!",
        'ref_week_prize': "🏆 <b>साप्ताहिक रेफरल चैंपियन!</b>\n\n<blockquote>🏅 आप पिछले हफ्ते <b>#{rank}</b> पर रहे, <b>{n}</b> एक्टिव रेफरल के साथ।\n🎁 इनाम: <b>+{days} दिन</b> प्रीमियम\n📅 वैधता: <b>{date}</b> तक</blockquote>\n\n🔥 नया हफ्ता शुरू हो गया। बुलाते रहें!",
        'ref_share_text': '🎁 इस बॉट से जुड़ें और टेलीग्राम पर फिल्में और सीरीज़ देखें!',
        'b_share': '📤 दोस्तों को शेयर करें',
        'share_text': '🎬 इसे टेलीग्राम पर देखें!',
        'status': '📋 <b>आपकी स्थिति</b>\n\n<blockquote>💎 <b>प्लान:</b> {plan}\n🎁 <b>ट्रायल:</b> {trial}\n🔓 <b>एक्सेस:</b> {access}\n📥 <b>आज के फ्री लिंक:</b> {free}</blockquote>',
        'st_free': "फ्री", 'st_prem': "प्रीमियम · {date} तक",
        'st_trial_on': "दिन {day}/{days} · आज {left}/{daily} लिंक बाकी",
        'st_trial_new': "अभी शुरू नहीं हुआ", 'st_trial_end': "खत्म", 'st_trial_off': "उपलब्ध नहीं",
        'st_acc_time': "वेरिफाइड · {time} तक", 'st_acc_credit': "{creds} क्रेडिट", 'st_acc_none': "वेरिफाई नहीं है",
        'st_acc_open': "सबके लिए खुला",
        'st_free_left': "{left}/{limit} बाकी",
        'generating': "⏳ आपका सुरक्षित लिंक बन रहा है...",
        'locked_trial_end': "🔒 <b>आपका फ्री ट्रायल खत्म हो गया है</b>",
        'locked_trial_today': "🔒 <b>आज के फ्री ट्रायल लिंक पूरे हो गए</b>",
        'locked_normal': "🔒 <b>वेरिफिकेशन ज़रूरी है</b>",
        'locked_body': '{head}\n\n<blockquote>🔓 <b>फ्री वेरिफाई</b> — {benefit}\n💎 <b>प्रीमियम</b> — तुरंत और बिना विज्ञापन एक्सेस</blockquote>\n\n👇 <i>नीचे दिया बटन दबाएं</i>',
        'benefit_time': "{hours} घंटे का फ्री एक्सेस", 'benefit_credit': "{creds} फ़ाइल लिंक",
        'ver_ok_time': '✅ <b>वेरिफाई हो गया!</b>\n\n<blockquote>⏳ अब <b>{duration} घंटे</b> तक एक्सेस मिलेगा।</blockquote>',
        'ver_ok_credit': '✅ <b>वेरिफाई हो गया!</b>\n\n<blockquote>🎁 <b>{creds}</b> फ़ाइल क्रेडिट जुड़ गए।</blockquote>',
        'ver_ok_nofile': "\n\nफ़ाइलें पाने के लिए अपना फ़ाइल लिंक दोबारा खोलें।",
        'already_active': "✅ आपका एक्सेस पहले से चालू है। जारी रखने के लिए अपना फ़ाइल लिंक खोलें।",
        'trial_note': "🎁 फ्री ट्रायल · दिन {day}/{days} · आज {left}/{daily} लिंक बाकी",
        'trial_last': "🎁 आज का आपका आखिरी ट्रायल लिंक था। कल फिर आएं, या और के लिए फ्री वेरिफाई / प्रीमियम चुनें।",
        'pay_caption': '💳 <b>चुना हुआ प्लान:</b> {plan}\n\n<blockquote>📱 QR कोड स्कैन करें या इस UPI ID पर पेमेंट करें\n<code>{upi}</code></blockquote>\n\n✅ पेमेंट के बाद <b>मैंने पेमेंट कर दिया</b> दबाएं और स्क्रीनशॉट भेजें।',
        'ask_ss': '📸 <b>अब अपना पेमेंट स्क्रीनशॉट भेजें</b>\n\n🪙 प्लान: {plan}',
        'ss_got': '✅ <b>स्क्रीनशॉट मिल गया!</b>\n\n⏳ आपका पेमेंट जांचा जा रहा है। अप्रूव होते ही आपको यहीं मैसेज मिलेगा।',
        'ss_pending': "⏳ आपका पेमेंट पहले से जांच में है। कृपया थोड़ा इंतज़ार करें।",
        'ss_bad': "कृपया अपने पेमेंट का फोटो (स्क्रीनशॉट) भेजें।",
        'approved': '🎉 <b>प्रीमियम चालू हो गया!</b>\n\n<blockquote>🪙 <b>प्लान:</b> {plan}\n📅 <b>वैधता:</b> {date} तक</blockquote>\n\n⚡ तुरंत और बिना विज्ञापन एक्सेस का आनंद लें।',
        'approved_diff': "🎉 <b>प्रीमियम चालू हो गया!</b>\n\nआपने {sel} चुना था, पर आपका पेमेंट <b>{plan}</b> से मेल खाया, इसलिए वही प्लान चालू किया गया है।\nवैधता: <b>{date}</b> तक\n\nलंबा प्लान चाहिए? प्लान अपग्रेड करें दबाएं।",
        'rejected': "❌ हम आपका पेमेंट वेरिफाई नहीं कर पाए।\n\nअगर आपने पेमेंट किया है, तो स्क्रीनशॉट के साथ सपोर्ट से संपर्क करें।",
        'exp_soon': '⏰ <b>प्रीमियम जल्द खत्म हो रहा है</b>\n\n<blockquote>आपका प्रीमियम <b>{days} दिन</b> में, {date} को खत्म होगा।</blockquote>\n\n🔁 तुरंत और बिना विज्ञापन एक्सेस जारी रखने के लिए अभी रिन्यू करें।',
        'prem_gone': "प्रीमियम अभी उपलब्ध नहीं है।",
    },
}


# ---------------------------------------------------------------------------
# Languages (picker order). Native names are shown on the picker buttons.
# ---------------------------------------------------------------------------
LANGS = [
    ('en', 'English'), ('hi', 'हिन्दी'), ('bn', 'বাংলা'), ('mr', 'मराठी'),
    ('te', 'తెలుగు'), ('ta', 'தமிழ்'), ('gu', 'ગુજરાતી'), ('ur', 'اردو'),
    ('kn', 'ಕನ್ನಡ'), ('ml', 'മലയാളം'), ('pa', 'ਪੰਜਾਬੀ'), ('or', 'ଓଡ଼ିଆ'),
]
LANG_CODES = [c for c, _ in LANGS]
LANG_NAMES = dict(LANGS)
LANG_NAMES_EN = {'en': 'English', 'hi': 'Hindi', 'bn': 'Bengali', 'mr': 'Marathi', 'te': 'Telugu', 'ta': 'Tamil',
                 'gu': 'Gujarati', 'ur': 'Urdu', 'kn': 'Kannada', 'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia'}


def detect_lang(code):
    """Telegram language_code -> supported code, or None (English / unknown = no suggestion)."""
    c = (code or '').lower().replace('_', '-').split('-')[0]
    return c if c in LANG_NAMES and c != 'en' else None


# ---------------------------------------------------------------------------
# New keys: script.py messages, reminder, cards, win-back, offers (English + Hindi)
# English re-uses your script.py text, so your edits there still apply.
# ---------------------------------------------------------------------------
from script import Script as _S

STR['en'].update({
    's_auto_deleted': _S.AUTO_DELETE_DONE, 's_invalid_link': _S.INVALID_LINK,
    's_batch_sending': _S.BATCH_SENDING, 's_batch_ok': _S.BATCH_SUCCESS, 's_batch_ok_warn': _S.BATCH_SUCCESS_WARN,
    's_file_nf': _S.FILE_NOT_FOUND_SERVER, 's_msg_nf': _S.MSG_NOT_FOUND_SERVER,
    's_single_warn': _S.SINGLE_SUCCESS_WARN, 's_delivery_err': _S.DELIVERY_ERROR,
    's_bypass': _S.BYPASS_DETECTED, 's_verify_invalid': _S.VERIFY_INVALID, 's_guard_banned': _S.GUARD_BANNED,
    's_banned': _S.BANNED_MSG, 's_banned_cb': _S.BANNED_CB_MSG, 's_banned_alert': _S.BANNED_CB_ALERT,
    's_private': _S.PRIVATE_MODE_MSG, 's_fsub_warn': _S.FSUB_WARNING,
    's_fsub_no': _S.FSUB_NOT_JOINED_ALERT, 's_fsub_ok': _S.FSUB_JOINED_ALERT,
    'b_join_ch': _S.BTN_JOIN_CHANNEL, 'b_check_joined': _S.BTN_CHECK_JOINED,
    'reminder': REMINDER_EN, 'card_duo': PREMIUM_CARD_EN, 'card_solo': PREMIUM_SOLO_EN,
    'locked_body': '{head}\n\n<blockquote>🔓 <b>Free Verify</b> — {benefit}\n💎 <b>Premium</b> — instant, ad-free access{offer}</blockquote>\n\n👇 <i>Tap a button below</i>',
    'offer': "\n💰 From just <b>₹{price}</b> · no waiting, no ads",
    'best_line': "⭐ <b>Best value:</b> {plan} · only ≈ ₹{pd}/day",
    'social': "🔥 <b>{n}</b> new members joined this week",
    'winback': "💔 <b>We miss you!</b>\n\n<blockquote>Your Premium ended <b>{days}</b> day(s) ago.\nRenew now to get instant, ad-free access again.</blockquote>",
    'u_d': "{n} Day|{n} Days", 'u_m': "{n} Month|{n} Months", 'u_y': "{n} Year|{n} Years",
})

STR['hi'].update({
    's_auto_deleted': "<blockquote>🗑 <b>आपकी फ़ाइलें अपने-आप डिलीट कर दी गई हैं!</b></blockquote>",
    's_invalid_link': "<blockquote>❌ <b>यह लिंक अमान्य है या एक्सपायर हो चुका है!</b></blockquote>",
    's_batch_sending': "<blockquote>⏳ <b>{total_files} फ़ाइलें भेजी जा रही हैं... कृपया प्रतीक्षा करें!</b></blockquote>",
    's_batch_ok': "<blockquote>✅ <b>आपकी सभी फ़ाइलें सफलतापूर्वक भेज दी गई हैं!</b></blockquote>",
    's_batch_ok_warn': "<blockquote>✅ <b>आपकी सभी फ़ाइलें सफलतापूर्वक भेज दी गई हैं!</b>\n\n⚠️ <b>चेतावनी:</b> स्पैम रोकने के लिए ये फ़ाइलें <b>{auto_delete_time} मिनट</b> में डिलीट हो जाएंगी। कृपया अभी फ़ॉरवर्ड कर लें।</blockquote>",
    's_file_nf': "<blockquote>❌ <b>फ़ाइल सर्वर पर नहीं मिली!</b></blockquote>",
    's_msg_nf': "<blockquote>❌ <b>मैसेज सर्वर पर नहीं मिला!</b></blockquote>",
    's_single_warn': "<blockquote>⚠️ <b>चेतावनी:</b> स्पैम रोकने के लिए यह फ़ाइल <b>{auto_delete_time} मिनट</b> में अपने-आप डिलीट हो जाएगी। कृपया अभी फ़ॉरवर्ड कर लें।</blockquote>",
    's_delivery_err': "<blockquote>❌ <b>डिलीवरी के दौरान एक त्रुटि हुई!</b></blockquote>",
    's_bypass': "<blockquote>🚫 <b>बायपास पकड़ा गया!</b>\n\nआपने बायपास टूल इस्तेमाल किया या गलत लिंक डाला है।\n\n<b>कृपया लिंक फिर से खोलें और ईमानदारी से वेरिफाई करें।</b></blockquote>",
    's_verify_invalid': "<blockquote>❌ <b>वेरिफिकेशन टोकन अमान्य या एक्सपायर है!</b>\nकृपया असली लिंक खोलकर दोबारा वेरिफाई करें।</blockquote>",
    's_guard_banned': "<blockquote>🚫 <b>बायपास टूल पकड़ा गया!</b>\nअमान्य सिग्नेचर! आपने लिंक को मैन्युअली बायपास करने की कोशिश की।</blockquote>",
    's_banned': "<blockquote>❌ <b>माफ़ कीजिए! आपको इस बॉट से हमेशा के लिए बैन कर दिया गया है।</b>\n\nमदद के लिए सपोर्ट से संपर्क करें।</blockquote>",
    's_banned_cb': "<blockquote>❌ <b>माफ़ कीजिए! आपको इस बॉट से बैन कर दिया गया है।</b></blockquote>",
    's_banned_alert': "❌ आप इस बॉट से बैन हैं!",
    's_private': "<blockquote>🔒 <b>माफ़ कीजिए! बॉट अभी प्राइवेट मोड में है।</b>\nएडमिन के पब्लिक करने पर आप फ़ाइलें पा सकेंगे।</blockquote>",
    's_fsub_warn': "<blockquote>⚠️ <b>फ़ाइल पाने के लिए नीचे दिए चैनल जॉइन करना ज़रूरी है!</b>\n\n<i>(ये जॉइन लिंक 10 मिनट में अपने-आप हट जाएंगे)</i></blockquote>",
    's_fsub_no': "⚠️ आपने अभी सभी चैनल जॉइन नहीं किए हैं! कृपया जॉइन करें।",
    's_fsub_ok': "✅ चैनल वेरिफिकेशन सफल!",
    'b_join_ch': "🟢 चैनल जॉइन करें {idx}", 'b_check_joined': "🔄 जॉइन चेक करें",
    'reminder': REMINDER_HI, 'card_duo': PREMIUM_CARD_HI, 'card_solo': PREMIUM_SOLO_HI,
    'locked_body': '{head}\n\n<blockquote>🔓 <b>फ्री वेरिफाई</b> — {benefit}\n💎 <b>प्रीमियम</b> — तुरंत और बिना विज्ञापन एक्सेस{offer}</blockquote>\n\n👇 <i>नीचे दिया बटन दबाएं</i>',
    'offer': "\n💰 सिर्फ़ <b>₹{price}</b> से · न इंतज़ार, न विज्ञापन",
    'best_line': "⭐ <b>सबसे बढ़िया वैल्यू:</b> {plan} · सिर्फ़ ≈ ₹{pd}/दिन",
    'social': "🔥 इस हफ्ते <b>{n}</b> नए मेंबर जुड़े",
    'winback': "💔 <b>हमें आपकी याद आई!</b>\n\n<blockquote>आपका प्रीमियम <b>{days}</b> दिन पहले खत्म हुआ।\nअभी रिन्यू करें और फिर से तुरंत, बिना विज्ञापन एक्सेस पाएं।</blockquote>",
    'u_d': "{n} दिन|{n} दिन", 'u_m': "{n} महीना|{n} महीने", 'u_y': "{n} साल|{n} साल",
})

STR['en'].update({'perks': '✨ <b>What you get</b>\n🚫 No ads\n✅ No verification, ever\n⚡ Direct files, instantly\n💾 Forward &amp; Save allowed\n♾️ Unlimited access\n', 'perk_duo': '🤖 One plan works in both bots\n'})

STR['hi'].update({'perks': '✨ <b>आपको क्या मिलेगा</b>\n🚫 कोई विज्ञापन नहीं\n✅ कभी वेरिफिकेशन नहीं\n⚡ सीधी फ़ाइलें, तुरंत\n💾 फ़ॉरवर्ड और सेव की छूट\n♾️ अनलिमिटेड एक्सेस\n', 'perk_duo': '🤖 एक प्लान, दोनों बॉट में\n'})

# Other languages live in utils/langs/<code>.py (each exposes a STR dict with the same keys).
import importlib as _il
for _c in LANG_CODES[2:]:
    try:
        STR[_c] = _il.import_module(f'utils.langs.{_c}').STR
    except ImportError:
        pass


def tr(lang: str, key: str, **kw) -> str:
    table = STR.get(lang) or STR['en']
    text = table.get(key)
    if text is None:
        text = STR['en'].get(key, key)
    return text.format(**kw) if kw else text


def plan_auto(lang: str, days: int) -> str:
    """'1 Month' / '3 Months' / '1 Year' in the user's language, built from days."""
    days = int(days)
    if days >= 365 and days % 365 == 0:
        key, n = 'u_y', days // 365
    elif days >= 30 and days % 30 == 0:
        key, n = 'u_m', days // 30
    else:
        key, n = 'u_d', days
    one, _, many = tr(lang, key).partition('|')
    return (one if n == 1 else (many or one)).format(n=n)
