from django.apps import AppConfig

class Telegram_botConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
        import telegram_bot.signals