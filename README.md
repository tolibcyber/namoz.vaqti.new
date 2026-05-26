# 🕌 Namoz Vaqtlari Bot

Telegram Mini App + Bot

## Fayllar
- `namoz_bot.py` — Telegram bot
- `index.html` — Mini App (GitHub Pages ga deploy qiling)

## Deploy qilish

### 1. GitHub Pages (Mini App uchun)
1. GitHub da yangi repo oching
2. `index.html` ni repo ga yuklang
3. Settings → Pages → Branch: main → Save
4. URL: `https://username.github.io/repo-name`

### 2. Railway (Bot uchun)
1. railway.app ga kiring
2. "New Project" → "Deploy from GitHub repo"
3. Repo ni tanlang
4. Variables ga qo'shing:
   - `BOT_TOKEN` = BotFather dan olgan token
   - `ADMIN_ID` = Sizning Telegram ID ingiz
   - `MINI_APP_URL` = GitHub Pages URL (yuqoridagi 4-qadam)

### 3. BotFather sozlamalari
BotFather da:
- `/setmenubutton` → botni tanlang → Mini App URL ni kiriting
- `/setdomain` → GitHub Pages domenini tasdiqlang

## .env (local test uchun)
```
BOT_TOKEN=...
ADMIN_ID=...
MINI_APP_URL=https://username.github.io/namoz-app
```
