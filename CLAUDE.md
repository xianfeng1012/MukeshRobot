# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 Commands

All work happens in the `projects/` directory.

```bash
cd projects

# Configure environment
cp .env.example .env          # then edit tokens/secrets

# Build & run the full stack (MongoDB, Redis, shared-api, 3 bots)
docker-compose up -d
docker-compose ps
docker-compose logs -f [shared-api|group-bot|miniapp-bot|user-bot]
docker-compose down

# Rebuild after code/dependency changes
docker-compose build [service]          # then: docker-compose up -d [service]
docker-compose build --no-cache         # full clean rebuild

# Health check
curl http://localhost:5000/health
```

There is **no test suite, linter, or build step** beyond Docker image builds. The only fast local check is a Python syntax compile:

```bash
python -m py_compile shared_api/app.py group_bot/*.py miniapp_bot/*.py user_bot/*.py
```

### Production deployment
The stack runs on a Baota (宝塔) server under `/opt/apps/telegram-bot/` using **Docker Compose v2** (`docker compose`, no hyphen). Deploy by copying changed files there and running `docker compose build <svc> && docker compose up -d <svc>`. Do not publish MongoDB/Redis host ports there — the host already runs native `mongod`/`redis-server` on 27017/6379, so those `ports:` mappings are intentionally removed in the deployed compose file (bots reach them over the internal Docker network only).

## 🏗️ Architecture

Four services share MongoDB + Redis. **`shared_api` (Flask) is the data hub** for `group_bot` and `user_bot`; **`miniapp_bot` does NOT use `shared_api` for points** — it talks to an external project's API (see below).

```
                 ┌──────────── shared_api (Flask, :5000) ────────────┐
                 │  MongoDB (users, group_settings, group_members,   │
                 │  blacklist, activity_logs) + Redis cache          │
                 └───────────────────────────────────────────────────┘
                      ▲                          ▲
              group_bot                      user_bot
         (verification, moderation)     (profiles, activity)

   miniapp_bot ──► yanyulou external API (https://.../api/bot/*, X-API-Key)
        (points / sign-in / leaderboard live in yanyulou's Postgres, NOT here)
```

- **Bot ↔ shared_api auth:** header `X-Bot-Token` must equal the shared secret `API_BOT_TOKEN` (a single fixed string for all bots; *not* a Telegram token, *not* JWT). JWT (`JWT_SECRET`, HS256) exists only for Mini App access tokens.
- **Inside containers** reference services by name (`mongodb:27017`, `redis:6379`, `http://shared-api:5000/api`). MongoDB is schema-less; no migrations.

### shared_api (`shared_api/app.py`)
REST endpoints under `/api`: users + points + add-points, blacklist, activity-log, leaderboard, **group settings** (`/api/groups/<chat_id>/settings`), and **group members / probation** (`/api/group-members`, `.../expired?days=N`). `models.py` holds Pydantic models. Endpoints are guarded by the `bot_token_required` decorator.

### group_bot — group management (most complex service)
Token-gated, **per-group, persistent** behavior. The key pattern: handlers are **always registered**; their behavior is decided **at runtime** by per-group settings fetched from `shared_api` (cached ~30s), not by startup config flags. Two toggles per group, persisted in the `group_settings` collection and flipped by admin commands:
- `verify_enabled` (`/toggleverify`) — **math-captcha verification**. New member is fully muted; the group message has a **deep-link button** (`https://t.me/<bot>?start=verify_<chatId>_<userId>`) that opens a **private chat** with the bot; the bot poses a multiple-choice math question and only unmutes on a correct answer (retries until correct). A `JobQueue` timeout kicks users who never verify.
- `spam_enabled` (`/togglespam`) — the **anti-spam suite** (this replaced the old keyword/ad-word filter, which was removed):
  - **New-member probation:** members are text-only for `PROBATION_DAYS` (default 3). Join time + status live in the `group_members` collection; an hourly `JobQueue.run_repeating` job (`graduate_probation_users`) restores media permissions after the period.
  - **Link/forward deletion:** any non-admin message containing a URL/`text_link` entity or a forward is deleted (`moderate_message`).
- `/setwelcome <text>` sets a per-group welcome (`{user}` placeholder). All three admin commands check `is_user_admin`.
- **Slash-command auto-delete:** a handler registered in **handler group 1** (`MessageHandler(filters.COMMAND & filters.ChatType.GROUPS, ...)`) deletes every user slash command in groups after 2 min. It is in a separate handler group so it runs *in addition to* the real `CommandHandler`s in group 0.

Permission constants in `handlers.py`: `MUTED_PERMISSIONS` (captcha), `PROBATION_PERMISSIONS` (text-only), `NORMAL_PERMISSIONS` (full). Use the **granular** `can_send_photos/videos/...` fields — `can_send_media_messages` is deprecated in PTB 20.x and media perms are independent of `can_send_messages`.

### miniapp_bot — points/gamification, integrates the **yanyulou** project
Points, sign-in, and leaderboard are **not stored locally** — they live in the external *yanyulou* project (NestJS + Postgres, `User.points` keyed by `telegramId`). `handlers.py` calls its bot API via `yanyulou_api()` using `YANYULOU_API_BASE` + header `X-API-Key: YANYULOU_API_KEY`:
- `/points`, `/stats` → `GET /api/bot/points/{telegramId}`; `/leaderboard` → `GET /api/bot/rank`.
- `/checkin` → `POST /api/bot/sign-in {telegramId}` (yanyulou owns the once-per-day + streak point table; do not re-implement it here).
- `/play` opens the Mini App via a plain URL button to `MINIAPP_URL` (a `https://t.me/<bot>/app` link — a t.me link cannot be a `web_app` button).
- Display **nicknames, not usernames:** `get_display_name()` resolves `first_name`+`last_name` via `bot.get_chat()` (cached), because yanyulou's `telegramName` actually stores the @username.
- **Group auto-delete:** `/checkin /points /leaderboard /stats /tasks` delete both command and reply after 2 min in groups (private untouched), via `application.create_task` + `asyncio.sleep` (`reply_clean`/`_schedule_delete`). `utils.py` (old JWT token gen) is no longer used.

### user_bot
Profiles, activity logs, achievements, statistics, privacy — all via `shared_api` with the same `X-Bot-Token` pattern.

## 🔑 Conventions & gotchas

- **python-telegram-bot v20.3** everywhere. Import `ParseMode` from `telegram.constants`; use lowercase `filters` from `telegram.ext` (`filters.TEXT & ~filters.COMMAND`, `filters.StatusUpdate.NEW_CHAT_MEMBERS`).
- **JobQueue requires the extra.** `group_bot/requirements.txt` pins `python-telegram-bot[job-queue]==20.3`. Without it `application.job_queue` is `None` and `run_once`/`run_repeating` raise — this silently broke verification timeouts before. `miniapp_bot` deliberately avoids JobQueue and uses `asyncio` for delayed deletes.
- **Forwards** are detected via `message.forward_date` (PTB 20.3 predates `forward_origin`).
- **Bot must be a group admin** (with delete + restrict rights) for moderation, verification muting, link/command deletion to work. An admin bot also receives all group messages regardless of privacy mode.
- **Logging:** containers log to stdout (`StreamHandler`). Do not add `FileHandler` in Docker (causes `IsADirectoryError` when a log path is a mounted directory). `miniapp_bot/main.py` still has a `FileHandler` — leave the deployed `/tmp` paths intact.
- The `version:` key in `docker-compose.yml` is obsolete and emits a harmless warning under Compose v2.

## 🔧 Env vars (`.env`)
Bot tokens: `GROUP_BOT_TOKEN`, `MINIAPP_BOT_TOKEN`, `USER_BOT_TOKEN`. Shared secret: `API_BOT_TOKEN`. Mini App: `MINIAPP_URL`, `JWT_SECRET`. yanyulou integration (with working defaults in `miniapp_bot/config.py`): `YANYULOU_API_BASE`, `YANYULOU_API_KEY`. MongoDB/Redis URLs and most service settings are hardcoded in `docker-compose.yml`'s `environment:` blocks (only the secrets above are `${...}`-substituted from `.env`).
