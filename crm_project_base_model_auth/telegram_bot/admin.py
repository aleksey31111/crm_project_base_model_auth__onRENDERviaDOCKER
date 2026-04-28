from django.contrib import admin
from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__email', 'chat_id')