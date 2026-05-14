# Books Daily Updates — Setup Guide

Get daily book chapter summaries delivered to your phone or inbox.

---

## Quick Start

```bash
# 1. Copy env template and fill in your credentials
copy .env.example .env

# 2. One-click start (creates venv, installs deps, generates samples)
start.bat
```

App runs at **http://localhost:8000** — open in browser.

---

## Step 1: Fill in your credentials

Edit `.env` with your notification credentials for each channel you want.

### 📧 Email (Gmail SMTP)

1. Go to your Google Account → **Security** → **2-Step Verification** → Turn it **ON**
2. Go to **App Passwords** (https://myaccount.google.com/apppasswords)
3. Select app: **Mail**, device: **Other** → name it `Books Daily`
4. Copy the 16-character password (spaces are fine)
5. In `.env`:
   ```
   SMTP_EMAIL=your.email@gmail.com
   SMTP_PASSWORD=aaaa bbbb cccc dddd
   ```

### 🤖 Telegram

1. Open Telegram → search for **@BotFather**
2. Send `/newbot` → choose a name (e.g. `Books Daily`) → choose a username (e.g. `BooksDailyBot`)
3. Copy the HTTP API token (looks like `123456789:ABCdef...`)
4. In `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmNOPqrstUVwxyz
   ```
5. Start a chat with your bot, send `/start`
6. Find your Chat ID:
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Look for `"chat":{"id":123456789}` — that's your Chat ID
7. On the **Settings** page in the app, enter this Chat ID

### 💬 Twilio WhatsApp

1. Sign up at https://twilio.com
2. Go to Console → copy **Account SID** and **Auth Token**
3. Go to **Messaging → Try it out → Send a WhatsApp message**
4. Activate the Sandbox (send the join code to the provided number)
5. In `.env`:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_WHATSAPP_NUMBER=+14155238886
   ```

---

## Step 2: Upload Books

Click **Books** in the app → upload an Excel file.

### Excel format
The parser auto-detects columns. Create columns with headers like any of:
- `title`, `book`, `name`, `book_name`, `book title`
- `author`, `writer`
- `chapter`, `chapters`, `total chapters`, `total_chapters`

| title           | author       | total_chapters |
|-----------------|-------------|----------------|
| Atomic Habits   | James Clear | 20             |
| Deep Work       | Cal Newport | 10             |
| The Alchemist   | Paulo Coelho| 15             |

Two sample files are auto-generated on first run in `backend/data/`.

---

## Step 3: Schedule a Reading Plan

Go to **Dashboard** → click **Schedule** on any book.

This creates a daily plan: one chapter per day starting tomorrow at your chosen notification time.

---

## Step 4: Configure Notifications

Go to **Settings** and fill in:
- Your email (if using email notifications)
- Telegram Chat ID (if using Telegram)
- WhatsApp number with country code e.g. `+919876543210` (if using WhatsApp)

Toggle on the channels you want → click **Save**.

---

## Step 5: Get Daily Summaries

At the time you set (default **08:30 IST**), the scheduler runs and:

1. Picks the next unread chapter for each scheduled book
2. Generates a summary (AI local fallback — no API needed)
3. Sends via your enabled channels

---

## Test It Now

From the **Dashboard**, click **Send to My Phone** to trigger a one-time notification immediately.

---

## Monitoring

- **API Docs**: http://localhost:8000/docs
- **Logs**: Terminal output shows notification delivery status
- **DB**: `backend/data/books_daily.db` (SQLite)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Email not configured" | Check `SMTP_EMAIL` + `SMTP_PASSWORD` in `.env`, restart server |
| Telegram not sending | Verify `TELEGRAM_BOT_TOKEN` in `.env` and Chat ID on Settings page |
| WhatsApp not sending | Check Twilio sandbox is active and your number has joined |
| Scheduler not running | Ensure server stays running (keep terminal open) |
| No books shown | Upload an Excel file via the Books page |
| Chapter summary is short | That's the local fallback — set `HF_TOKEN` for better AI summaries |
