from django.core.management.base import BaseCommand
from user.views import bot

class Command(BaseCommand):
    help = 'Telegram Bot'

    def handle(self, *args, **options):
        bot.infinity_polling()