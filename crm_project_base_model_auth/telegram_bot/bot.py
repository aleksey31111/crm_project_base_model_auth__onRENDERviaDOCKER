import logging
from django.conf import settings
from django.urls import reverse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from contracts.models import Contract, Payment
from .models import TelegramUser

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    # Здесь нужно связать chat_id с пользователем Django по username/email.
    # Для упрощения: бот запрашивает токен или код подтверждения.
    await update.message.reply_text(
        "Привет! Я бот CRM. Для привязки аккаунта отправьте /bind ваш_логин_в_crm"
    )

async def bind(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /bind username")
        return
    username = args[0]
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        TelegramUser.objects.update_or_create(user=user, defaults={'chat_id': chat_id, 'is_active': True})
        await update.message.reply_text(f"Аккаунт {username} успешно привязан!")
    except User.DoesNotExist:
        await update.message.reply_text("Пользователь не найден")

async def payments(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    try:
        tg_user = TelegramUser.objects.get(chat_id=chat_id)
        user = tg_user.user
        # Последние 5 платежей по контрактам, где пользователь менеджер
        payments = Payment.objects.filter(contract__manager=user).order_by('-created_at')[:5]
        if not payments:
            await update.message.reply_text("Нет недавних платежей.")
            return
        text = "Последние платежи:\n"
        for p in payments:
            text += f"- {p.contract.number}: {p.amount}₽ ({p.payment_date})\n"
        await update.message.reply_text(text)
    except TelegramUser.DoesNotExist:
        await update.message.reply_text("Вы не привязали аккаунт. Используйте /bind username")

async def pay(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /pay contract_id")
        return
    contract_id = args[0]
    try:
        tg_user = TelegramUser.objects.get(chat_id=chat_id)
        user = tg_user.user
        contract = Contract.objects.get(id=contract_id, manager=user)
        # Генерируем ссылку на оплату (учебная)
        # Для реальной интеграции можно вызвать initiate-payment API
        fake_url = settings.BASE_URL + reverse('contracts:fake_payment_page', args=[contract.id])
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Оплатить", url=fake_url)
        ]])
        await update.message.reply_text(f"Ссылка для оплаты контракта {contract.number}:", reply_markup=keyboard)
    except Contract.DoesNotExist:
        await update.message.reply_text("Контракт не найден или у вас нет доступа")
    except TelegramUser.DoesNotExist:
        await update.message.reply_text("Привяжите аккаунт командой /bind username")

def send_telegram_notification(chat_id, message):
    """Отправка уведомления через бота (вызывать из сигналов)"""
    import asyncio
    # Для синхронного вызова используем asyncio.run() или threading
    # Упрощённо: можно отправить через requests к Telegram API
    # Здесь используем python-telegram-bot асинхронно, но в синхронном коде сложно.
    # Вместо этого используем прямой запрос к API:
    import requests
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        logger.error(f"Telegram send error: {e}")