from django.dispatch import Signal, receiver

import os

from .messege_manager import send_email
from .models import User

new_order = Signal()
confirm_order = Signal()


@receiver(new_order)
def new_order_signal(**signal_data):
    user = User.objects.get(id=signal_data['signal_data']['user_id'])
    subject = f'Order status updated'
    order_id = signal_data['signal_data']['order_id']
    body = f'You order #{order_id} is received.'
    admin_mail = os.getenv('EMAIL_ADMIN')
    receivers = [user.email, admin_mail]
    send_email(subject, body, receivers)


@receiver(confirm_order)
def new_order_signal(**signal_data):
    user = User.objects.get(id=signal_data['signal_data']['user_id'])
    subject = f'Order status updated'
    order_id = signal_data['signal_data']['order_id']
    body = f'You order #{order_id} is confirmed.'
    admin_mail = os.getenv('EMAIL_ADMIN')
    receivers = [user.email, admin_mail]
    send_email(subject, body, receivers)
