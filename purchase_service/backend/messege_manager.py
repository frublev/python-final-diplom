from django.core.mail import EmailMultiAlternatives
from purchase_service.settings import DEFAULT_FROM_EMAIL


def send_email(subject, body, receivers):
    sender = DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(subject, body, sender, receivers)
    msg.attach_alternative(body, "text/html")
    msg.send()
