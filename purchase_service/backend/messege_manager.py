from django.core.mail import EmailMultiAlternatives


def send_email(subject, body, sender, receivers):
    msg = EmailMultiAlternatives(subject, body, sender, receivers)
    msg.attach_alternative(body, "text/html")
    msg.send()
