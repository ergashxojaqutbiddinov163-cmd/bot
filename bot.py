import requests
import time

BOT_TOKEN = "7817700244:AAFU3GurkHhGQO5hLleryrrCZoOZPhmoL2I"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

OFFSET = None
ADMINS = [7982203142, 7666775420]

COURSES = {
    "arab": {"name": "Arab tili", "price": "450,000 so'm"},
    "ingliz": {"name": "Ingliz tili", "price": "450,000 so'm"},
    "rus": {"name": "Rus tili", "price": "460,000 so'm"},
    "tarix": {"name": "Tarix", "price": "450,000 so'm"},
    "turk": {"name": "Turk tili", "price": "450,000 so'm"},
}

HOURS = "🕒 Big Ben Arabic Learning Centre har kuni 08:00 – 22:00 gacha ishlaydi."
CREATOR_INFO = "👤 Bot yaratuvchisi: Ergashxo‘ja\n🔗 Username: @Ergashxoja_Qutbiddinov"

waiting_for_question = {}  # {admin_id: user_id}


# --- Telegram API yordamchi funksiyalar ---
def get_updates(offset=None):
    resp = requests.get(BASE_URL + "getUpdates", params={"offset": offset, "timeout": 30})
    return resp.json()

def send_message(chat_id, text, buttons=None, inline_buttons=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"keyboard": buttons, "resize_keyboard": True}
    if inline_buttons:
        payload["reply_markup"] = {"inline_keyboard": inline_buttons}
    requests.post(BASE_URL + "sendMessage", json=payload)

def edit_message(chat_id, message_id, text, inline_buttons=None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if inline_buttons:
        payload["reply_markup"] = {"inline_keyboard": inline_buttons}
    requests.post(BASE_URL + "editMessageText", json=payload)

def request_contact(chat_id):
    keyboard = {
        "keyboard": [[{"text": "📱 Telefon raqamni yuborish", "request_contact": True}]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    payload = {"chat_id": chat_id, "text": "Iltimos, telefon raqamingizni yuboring:", "reply_markup": keyboard}
    requests.post(BASE_URL + "sendMessage", json=payload)

def show_main_menu(chat_id):
    buttons = [["📚 Kurslar", "🕒 Ish vaqti"],
               ["❓ Savol berish", "ℹ️ Ma’lumot"]]
    send_message(chat_id, "📌 Asosiy menyu:", buttons=buttons)


# --- Asosiy logika ---
def handle_message(chat_id, text, message, username=None, name=None):
    global waiting_for_question
    text_clean = text.lower().strip() if text else ""

    # Admin reply
    if chat_id in ADMINS and chat_id in waiting_for_question:
        user_id = waiting_for_question[chat_id]
        send_message(user_id, f"📩 Admin javobi:\n\n{text}")
        send_message(chat_id, "✅ Javob foydalanuvchiga yuborildi.")
        waiting_for_question.pop(chat_id)
        return

    # Admin reply:USER_ID
    if chat_id in ADMINS and text_clean.startswith("reply:"):
        try:
            parts = text.split(" ", 1)
            target_id = int(parts[0].replace("reply:", "").strip())
            reply_text = parts[1] if len(parts) > 1 else ""
            send_message(target_id, f"📩 Admin javobi:\n\n{reply_text}")
            send_message(chat_id, f"✅ Javob foydalanuvchiga ({target_id}) yuborildi.")
        except Exception:
            send_message(chat_id, "⚠️ To‘g‘ri format: reply:USER_ID Javob matni")
        return

    # Start
    if text_clean == "/start":
        send_message(chat_id,
            "👋 Assalomu alaykum!\n\n"
            "Siz *Big Ben Arabic Learning Centre* rasmiy botiga xush kelibsiz.\n\n"
            "Avval telefon raqamingizni yuboring:"
        )
        request_contact(chat_id)
        return

    # Kurslar (inline tugmalar bilan)
    if text_clean == "📚 kurslar":
        inline_buttons = [[{"text": COURSES[key]["name"], "callback_data": f"course_{key}"}] for key in COURSES]
        send_message(chat_id, "📚 Bizning kurslar:", inline_buttons=inline_buttons)
        return

    # Ish vaqti
    if text_clean == "🕒 ish vaqti":
        send_message(chat_id, HOURS)
        return

    # Savol berish
    if text_clean == "❓ savol berish":
        send_message(chat_id, "Savolingizni yozib yuboring, admin sizga javob beradi.")
        for admin in ADMINS:
            send_message(admin, f"❓ Yangi savol {name or ''} (@{username or 'NoUser'}) dan keldi.\n"
                                f"ID: <code>{chat_id}</code>\n\n👉 Javob berish uchun shunchaki yozing.")
            waiting_for_question[admin] = chat_id
        return

    # Creator info
    if text_clean == "ℹ️ ma’lumot":
        send_message(chat_id, CREATOR_INFO)
        return


# --- Callbacklarni boshqarish ---
def handle_callback(callback):
    query_id = callback["id"]
    data = callback["data"]
    message = callback["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]

    if data.startswith("course_"):
        key = data.replace("course_", "")
        if key in COURSES:
            name = COURSES[key]["name"]
            price = COURSES[key]["price"]
            text = f"📚 <b>{name}</b>\n\n" \
                   f"💵 Kurs narxi: {price}\n" \
                   f"👨‍🏫 Individual: har bir soati 100,000 so'm"
            edit_message(chat_id, message_id, text)


# --- Botni ishga tushirish ---
from flask import Flask
import threading, os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running on Render!"

def run_bot():
    main()  # your infinite Telegram loop

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
