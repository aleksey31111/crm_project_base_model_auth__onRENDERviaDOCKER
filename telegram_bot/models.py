from django.db import models
from django.conf import settings

class TelegramUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='telegram_profile')
    chat_id = models.BigIntegerField(unique=True, verbose_name='Telegram chat ID')
    is_active = models.BooleanField(default=True, verbose_name='Получать уведомления')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    def __str__(self):
        return f"{self.user.username} - {self.chat_id}"