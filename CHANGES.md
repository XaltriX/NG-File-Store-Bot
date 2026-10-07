# What's new

1. Verified users count (today + yesterday, IST, unique users, auto-cleanup) in /stats and the Stats panel.
2. Dual shortner: S1/S2 rotate after each successful verify. Toggle, fallback to S1, per-shortner counts, masked API.
3. Free trial: 3 days, 5 links/day (IST), no force-sub, starts on first file link. Then free daily limit (3), then Verify / Premium.
4. Reminders every 12h (editable) to ended-trial unverified users. Quiet hours 11 PM - 8 AM IST, stops after 5 ignored.
5. Button-only UI: /start menu, Status, Language (English / Hindi), Admin Panel (/settings or Admin Panel button).
6. Premium: plans card, QR, screenshot, Approve (or approve a different plan) / Reject, expiry reminders, everything editable from the panel.

Old commands still work as hidden shortcuts. Env vars: see .env.example.

## Security cleanup (original author's hardcoded values removed)
- OWNER_ID now comes from env (was hardcoded to the original developer's ID). Bot refuses to start without it.
- Web guard no longer points to the original developer's Cloudflare worker. It needs your own GUARD_URL + GUARD_SECRET, otherwise it is off.
- File links are plain t.me/<bot>?start=... deep links. No website/pages domain is used anywhere.
- Support/Updates/Owner links, DB/LOG channels and the "Powered by" caption tag are now env-controlled and empty by default.

## Round 3
- Admin Panel: Users -> Premium list (8 per page, Active / Expiring tabs). Home -> Pending payments (approve/reject from the list).
- /stats: Premium now + ever, Verified now + ever (unique). Lifetime flags are filled automatically on first start.
- Broadcast targets: All / Premium (past + current) / Verified (past + current), with counts and optional auto-delete.
- "Contact Owner" button (full width, last row) on the plans screen, "under review" and "Premium activated" messages.
- Premium screen: "One payment. Two bots." card (shows both bot names only while Partner sync is ON).
- Partner bot sync through one shared mailbox MongoDB (Trial & Premium -> Partner bot). Grants only, never removals.
- Fixed: reply_to_message_id crash on new Kurigram; owner can now test the payment flow with their own account.

## Round 4 (sync made observable and robust)
- Partner screen now shows this bot's worker status AND the partner bot's worker status (heartbeat via the mailbox).
- "Sync now" button runs a full round instantly (works even if the toggle is OFF).
- Approve tells you "Partner bot notified" / "queued" / "partner sync is OFF".
- Background workers are started from the start hook AND from the first incoming update, so they cannot be missed.
- Sync events are printed in the logs ("Sync: sent / granted / error").

## Round 5
- "Share this" button under every delivered file (single file: on the file; batch: on the final "all files sent" message). Opens Telegram's share sheet with this post's link; text is English/Hindi by user language. Toggle: Admin Panel -> General -> Share button.

## Round 6 - Proof channel
- On approve, the payment screenshot is posted to the proof channel with: member name, plan, validity (days), bots, an engagement line, and [Buy Premium][Contact] buttons side by side.
- Each payment request has a "Post proof: ON/OFF" toggle (default ON) so you can approve without posting.
- Admin Panel -> Trial & Premium -> Proof channel: channel ID, ON/OFF, caption editor, test post.
- Only the bot where you approve posts. Premium granted by sync in the partner bot never posts.
- "Buy Premium" in the channel opens the plans screen via /start premium.

## Round 7 - Refer & Earn, share tracking, More Videos, single-file share fix
- Share button now travels WITH single files too (it was added afterwards by editing, which silently failed for copied messages).
- Share links carry the sharer's id (post_rf<id>); Refer & Earn screen has the personal link (start=ref_<id>). A new user counts for one sharer only.
- Every 5 referrals = 1 day Premium, instantly, in BOTH bots (referral events travel through the partner mailbox; keep Sync ON in both bots).
- Weekly top 5 (Monday 00:10 IST, previous week): +10/8/6/4/2 days. Only ACTIVE referrals (friend received a file) count; banned users are excluded.
- Admin Panel -> Trial & Premium -> Refer & Earn: ON/OFF, referrals per reward, days per reward, weekly bonus days, top 5 (week + lifetime). /stats shows "Joined via share today / lifetime".
- "More Videos" (Preview link) is the last full-width button on: welcome, verify screen, reminders, "last trial link" note, premium activated / under review / expiry notices, referral rewards.
- Your own config.py, runtime.txt and your text edits in utils/i18n.py are kept exactly as they were.
