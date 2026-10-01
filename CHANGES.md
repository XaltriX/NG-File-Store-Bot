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
