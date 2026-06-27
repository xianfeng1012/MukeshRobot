# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 Commands

All work happens in the `projects/` directory.

```bash
cd projects

# Configure environment
cp .env.example .env          # then edit tokens/secrets

# Build & run the full stack (MongoDB, Redis, shared-api, 4 bots)
docker-compose up -d
docker-compose ps
docker-compose logs -f [shared-api|group-bot|miniapp-bot|user-bot|dual-bot]
docker-compose down

# Rebuild after code/dependency changes
docker-compose build [service]          # then: docker-compose up -d [service]
docker-compose build --no-cache         # full clean rebuild

# Health check
curl http://localhost:5000/health
```

There is **no test suite, linter, or build step** beyond Docker image builds. The only fast local check is a Python syntax compile:

```bash
python -m py_compile shared_api/app.py group_bot/*.py miniapp_bot/*.py user_bot/*.py dual_bot/*.py
```

### Production deployment
The stack runs on a Baota (宝塔) server under `/opt/apps/telegram-bot/` using **Docker Compose v2** (`docker compose`, no hyphen). Deploy by `scp`-ing changed files there and running `docker compose up -d --build <svc>`. Do not publish MongoDB/Redis host ports there — the host already runs native `mongod`/`redis-server` on 27017/6379, so those `ports:` mappings are intentionally removed (bots reach them over the internal Docker network only). The `.env` on the server holds the real tokens and is **not** in git; when adding env vars, update both `.env` (real values) and `.env.example` (placeholders), and add the `${VAR}` line to the relevant service's `environment:` block in `docker-compose.yml`.

## 🏗️ Architecture

Five services share MongoDB + Redis. **`shared_api` (Flask) is the data hub** for `group_bot` and `user_bot`; **`miniapp_bot` does NOT use `shared_api` for points** — it talks to the external *yanyulou* project's API; **`dual_bot` is fully standalone** (only MongoDB, no shared_api/yanyulou).

```
                 ┌──────────── shared_api (Flask, :5000) ────────────┐
                 │  MongoDB (users, group_settings, group_members,   │
                 │  blacklist, activity_logs) + Redis cache          │
                 └───────────────────────────────────────────────────┘
                      ▲                          ▲
              group_bot                      user_bot
         (verification, moderation)     (profiles, activity, 导航/菜单)

   miniapp_bot ──► yanyulou external API (https://.../api/bot/*, X-API-Key)
        (points / sign-in / leaderboard / 今日开课 ACTIVE girls live in yanyulou's Postgres)

   dual_bot ──► MongoDB only (dual_relay collection); N customer-facing bots, one support group
```

- **Bot ↔ shared_api auth:** header `X-Bot-Token` must equal the shared secret `API_BOT_TOKEN` (a single fixed string for all bots; *not* a Telegram token, *not* JWT). JWT (`JWT_SECRET`, HS256) exists only for Mini App access tokens.
- **Inside containers** reference services by name (`mongodb:27017`, `redis:6379`, `http://shared-api:5000/api`). MongoDB is schema-less; no migrations.

### shared_api (`shared_api/app.py`)
REST endpoints under `/api`: users + points + add-points, blacklist, activity-log, leaderboard, **group settings** (`/api/groups/<chat_id>/settings`), and **group members / probation** (`/api/group-members`, `.../expired?days=N`). `models.py` holds Pydantic models. Endpoints are guarded by the `bot_token_required` decorator.

### group_bot — group management (most complex service)
Token-gated, **per-group, persistent** behavior. Handlers are **always registered**; behavior is decided **at runtime** by per-group settings fetched from `shared_api` (cached ~30s). Two toggles per group (`group_settings` collection), flipped by admin commands `/toggleverify` / `/togglespam`:
- `verify_enabled` — **关注频道验证 (channel-follow verification)**. New member is fully muted (`MUTED_PERMISSIONS`); the in-group message has two buttons: a **URL button to `VERIFY_CHANNEL_LINK`** and a **callback button `cv_<chatId>_<userId>`**. On click, `handle_channel_verify` calls `getChatMember(VERIFY_CHANNEL_ID, user)` — **group_bot must be an admin of that channel** to query membership. If joined → unmute (probation or full per `spam_enabled`); else alert "请先关注频道". A `JobQueue` timeout kicks users who never verify. (The old private-chat math captcha was **removed**.)
- `spam_enabled` — anti-spam suite: **new-member probation** (text-only for `PROBATION_DAYS`, default 3; hourly `graduate_probation_users` job restores media) + **link/forward deletion** (`moderate_message`).
- **New-member detection covers BOTH join paths:** `handle_new_member` (the `new_chat_members` service message — fires when someone is *added* by another user) **and** `handle_chat_member_update` (a `ChatMemberHandler` for `chat_member` updates — fires when a user *joins by themselves via invite link/search*, which emits **no** service message). Both call `process_new_member`, which dedupes via `_recently_processed` (60 s) so a join isn't processed twice. This requires `allowed_updates=Update.ALL_TYPES` **and** the bot being a group admin (Telegram only delivers `chat_member` updates to admin bots).
- **`moderate_message` must skip `message.is_automatic_forward`.** When a linked channel auto-forwards a post into its discussion group (the comment anchor, sender = Telegram service account `777000`), it looks like a non-admin forward; deleting it destroys the channel's comment section. The early `is_automatic_forward` guard prevents that.
- **Command deletion / reply lifetime:** `cleanup_group_command` (handler **group 1**) deletes a **non-admin** slash command immediately; an **admin** slash command is kept. Command **replies** auto-delete after 2 min in groups via `reply_autodel` (private chats untouched; user messages preserved).

Permission constants in `handlers.py`: `MUTED_PERMISSIONS` (verify), `PROBATION_PERMISSIONS` (text-only), `NORMAL_PERMISSIONS` (full). Use the **granular** `can_send_photos/videos/...` fields — `can_send_media_messages` is deprecated in PTB 20.x.

### miniapp_bot — points/gamification + 今日开课, integrates **yanyulou**
Points/sign-in/leaderboard live in the external *yanyulou* project (NestJS + Postgres, keyed by `telegramId`). `handlers.py` calls its bot API via `yanyulou_api()` (`YANYULOU_API_BASE` + header `X-API-Key`):
- `/points`,`/stats` → `GET /api/bot/points/{id}`; `/leaderboard` → `GET /api/bot/rank`; `/checkin` → `POST /api/bot/sign-in` (yanyulou owns the streak table).
- **`/schedule` + 汉字「今日开课」**: `GET /api/bot/girls/active` returns ACTIVE girls (`category`/`location`/`photo` etc.). Renders a **photo album** of avatars (FEATURED + NEWBIE only, PART_TIME excluded, chunked ≤10/album) **on top**, then **text** (names as `t.me/<bot>?start=girl_<id>` deep links grouped by category→location, city-filtered by `SCHEDULE_CITY`) **below**, plus 精品榜/兼职榜/新生榜 inline buttons. `_build_schedule_text` / `_collect_schedule_photos` are shared by the command and the scheduled job.
- **Daily 14:00 (Asia +8) `JobQueue.run_daily`** → `publish_schedule_to_channel` posts the same album+text to `SCHEDULE_CHANNEL_ID` (公示榜); **skips when no ACTIVE teachers**. miniapp_bot must be an admin of that channel.
- **Channel profile publishing:** `publish_profile_to_channel` (driven by a webhook on `:8000/publish-profile`) sends/edits per-girl media groups to the FEATURED/PART_TIME/NEWBIE channels (`CHANNEL_*`).
- Display **nicknames, not usernames** via cached `get_display_name()`. Group auto-delete (`reply_clean`) cleans command+reply after 2 min for sign-in/points/etc.

### user_bot — profiles + 导航/菜单/积分规则
Profiles, activity, achievements, statistics, privacy — all via `shared_api`. Added group-facing helpers:
- **`/pointsrules` + 汉字「积分规则」** → fixed points-rules text (`POINTS_RULES_TEXT`).
- **`/guide` + 汉字「导航」** → HTML message with anchor links (精品榜 / 小程序 / 群主 from `GUIDE_*` config) + inline buttons (精品榜|兼职榜|新生榜 URLs, and a `show_points_rules` callback button).
- **Bottom reply-keyboard menu** `[签到][导航][今日开课]` (`_menu_keyboard`, `is_persistent=True, selective=True`). Auto-popped to a new member on join (both `new_chat_members` and `chat_member`, deduped) and summonable by anyone via `/menu` or 汉字「菜单」 (so existing members can get it too). The buttons just emit plain text — **签到/今日开课 are answered by miniapp_bot**, 导航 by user_bot.

### dual_bot — multi-account two-way customer-service relay (standalone)
**N customer-facing bots run in one process** (`DUAL_BOT_TOKENS` = comma-separated token list; each gets its own PTB `Application`, started concurrently via asyncio in `main.py`). All feed **one shared support group** (`SUPPORT_GROUP_ID`) and one MongoDB (`dual_relay` collection, via `db.py`/pymongo — no shared_api).
- **Customer → group:** a customer DMs any bot → that bot posts an identity header `👤 name (@user / id) ·〔BotN〕` then `copy_message`s the original into the support group; the resulting group `message_id → customer_id` mapping is saved (header + content both).
- **Group → customer:** an operator **replies** (Telegram reply, not @mention) to a forwarded message → the source bot looks up the mapping and `copy_message`s the operator's content back to that customer. Non-reply group chatter is ignored.
- **Routing relies on privacy mode being ON:** a privacy-mode bot in a group only receives **replies to its own messages**, so each operator reply reaches only the source bot — no cross-talk, no dedup needed (the stored `bot_id` is a safety fallback).
- **Adding bots:** append the token to `DUAL_BOT_TOKENS`, add the new bot to the support group, restart. After an env change, `docker compose up -d dual-bot` can race during recreate (CancelledError, partial start) — follow with `docker compose restart dual-bot` for a clean start; confirm "DualBot 已启动 N 个机器人实例". `/id` (primary instance only) prints a chat id.

## 🔑 Conventions & gotchas

- **python-telegram-bot v20.3** everywhere. Import `ParseMode` from `telegram.constants`; use lowercase `filters` from `telegram.ext`.
- **`JobQueue` requires the `[job-queue]` extra.** `group_bot` and `miniapp_bot` pin `python-telegram-bot[job-queue]==20.3` (group_bot for verify timeout + probation; miniapp_bot for the 14:00 `run_daily`). Without the extra `application.job_queue` is `None`.
- **Private supergroup / channel IDs need the `-100` prefix for the Bot API.** A link like `t.me/+abc` or a raw id like `-4378375166` won't work with `getChatMember`/`send_message` — the real id is `-100` + the digits (e.g. `-1004378375166`). This bit us repeatedly (support group, verify channel). Verify a private id with `curl .../getChat?chat_id=-100...` before trusting it.
- **`chat_member` updates** (self-join detection, dual_bot reply routing nuances) require `allowed_updates=Update.ALL_TYPES` **and** the bot being a group admin. `new_chat_members` only fires when a member is *added by someone else*, not on self-join via link.
- **Bot must be a group admin** (delete + restrict rights) for moderation/verification/muting. An admin bot also receives all group messages regardless of privacy mode. group_bot must additionally be admin **of the verify channel** to check follow status; miniapp_bot must be admin of the publish/公示榜 channels.
- **Forwards** are detected via `message.forward_date` (PTB 20.3 predates `forward_origin`); **never delete `is_automatic_forward` messages** (channel comment anchors).
- **Reply keyboards** in groups: use `selective=True` (+ mention the target user) so the menu shows only to the intended member; `is_persistent=True` keeps it docked.
- **Logging:** containers log to stdout (`StreamHandler`). Avoid `FileHandler` in Docker. `miniapp_bot/main.py` still has a `/tmp` `FileHandler` — leave it.
- The `version:` key in `docker-compose.yml` is obsolete and emits a harmless warning under Compose v2.

## 🔧 Env vars (`.env`)
- **Bot tokens:** `GROUP_BOT_TOKEN`, `MINIAPP_BOT_TOKEN`, `USER_BOT_TOKEN`; `DUAL_BOT_TOKENS` (comma-separated list). Shared secret: `API_BOT_TOKEN`.
- **group_bot 关注频道验证:** `VERIFY_CHANNEL_ID` (`-100...`), `VERIFY_CHANNEL_LINK`, `VERIFY_CHANNEL_NAME`.
- **dual_bot:** `SUPPORT_GROUP_ID` (`-100...`).
- **miniapp_bot:** `MINIAPP_URL`, `JWT_SECRET`, `YANYULOU_API_BASE`, `YANYULOU_API_KEY` (working defaults in `miniapp_bot/config.py`); `SCHEDULE_CHANNEL_ID`, `SCHEDULE_CITY`, `CHANNEL_*` / `CHANNEL_LINK_*` (defaulted in config).
- **user_bot 导航:** `GUIDE_FEATURED_LINK`, `GUIDE_PARTTIME_LINK`, `GUIDE_NEWBIE_LINK`, `GUIDE_MINIAPP_LINK`, `GUIDE_OWNER_LINK` (defaulted in config).
- MongoDB/Redis URLs and most settings are hardcoded in `docker-compose.yml`'s `environment:` blocks; only secrets/ids above are `${...}`-substituted from `.env`.

> **Note:** `yanyulou`'s backend lives in a **separate repo** (`搬瓦工项目/yanyulou`, NestJS). `GET /api/bot/girls/active` there returns the ACTIVE girls (incl. `category`/`location`/`photo`) consumed by miniapp_bot's 今日开课. Changes to that endpoint are deployed from that repo, not this one.
