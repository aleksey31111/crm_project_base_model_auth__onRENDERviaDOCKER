from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler
from telegram_bot.bot import start, bind, payments, pay

class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        from django.conf import settings
        app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("bind", bind))
        app.add_handler(CommandHandler("payments", payments))
        app.add_handler(CommandHandler("pay", pay))
        self.stdout.write(self.style.SUCCESS("Бот запущен"))
        app.run_polling()