"""All user-facing texts (English default + Devanagari Hindi)."""

PREMIUM_CARD_EN = (
    "💎 <b>Choose Your Plan</b>\n\n"
    "<blockquote>🎁 <b>One payment. Two bots.</b>\n{bots}\n"
    "<i>Pay in either bot. Premium turns on in both.</i></blockquote>\n\n"
    "<b>How it works</b>\n1️⃣ Pick a plan → 2️⃣ Pay by UPI → 3️⃣ Send screenshot → 4️⃣ Done\n\n"
    "🚫 No ads · ✅ No verification · ⚡ Direct videos\n\n"
    "👇 <i>Pick a plan to continue</i>"
)

PREMIUM_CARD_HI = (
    "💎 <b>अपना प्लान चुनें</b>\n\n"
    "<blockquote>🎁 <b>एक पेमेंट। दो बॉट।</b>\n{bots}\n"
    "<i>किसी भी बॉट में पेमेंट करें। प्रीमियम दोनों में चालू होगा।</i></blockquote>\n\n"
    "<b>कैसे होगा</b>\n1️⃣ प्लान चुनें → 2️⃣ UPI से पेमेंट → 3️⃣ स्क्रीनशॉट भेजें → 4️⃣ हो गया\n\n"
    "🚫 कोई विज्ञापन नहीं · ✅ कोई वेरिफिकेशन नहीं · ⚡ सीधा वीडियो\n\n"
    "👇 <i>आगे बढ़ने के लिए प्लान चुनें</i>"
)

PREMIUM_SOLO_EN = (
    "💎 <b>Choose Your Plan</b>\n\n"
    "<b>How it works</b>\n1️⃣ Pick a plan → 2️⃣ Pay by UPI → 3️⃣ Send screenshot → 4️⃣ Done\n\n"
    "🚫 No ads · ✅ No verification · ⚡ Direct videos\n\n"
    "👇 <i>Pick a plan to continue</i>"
)

PREMIUM_SOLO_HI = (
    "💎 <b>अपना प्लान चुनें</b>\n\n"
    "<b>कैसे होगा</b>\n1️⃣ प्लान चुनें → 2️⃣ UPI से पेमेंट → 3️⃣ स्क्रीनशॉट भेजें → 4️⃣ हो गया\n\n"
    "🚫 कोई विज्ञापन नहीं · ✅ कोई वेरिफिकेशन नहीं · ⚡ सीधा वीडियो\n\n"
    "👇 <i>आगे बढ़ने के लिए प्लान चुनें</i>"
)

PROOF_CAPTION = (
    "╔═══ ✦ 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 ✦ ═══╗\n\n"
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
        'welcome': '✨ <b>Welcome, {name}!</b>\n\n<blockquote>🎬 Your home for K-Drama &amp; Movies.\nOpen any file link and your files arrive instantly.</blockquote>',
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
        'welcome': '✨ <b>नमस्ते {name}!</b>\n\n<blockquote>🎬 K-Drama और Movies का आपका अपना घर।\nकोई भी फ़ाइल लिंक खोलें और फ़ाइलें तुरंत पाएं।</blockquote>',
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


def tr(lang: str, key: str, **kw) -> str:
    table = STR.get(lang) or STR['en']
    text = table.get(key)
    if text is None:
        text = STR['en'].get(key, key)
    return text.format(**kw) if kw else text
