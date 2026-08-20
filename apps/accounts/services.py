from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailService:
    @staticmethod
    def send_email(to_email, subject, template_name, context):
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=None,
            recipient_list=[to_email],
            html_message=html_message,
        )

    @staticmethod
    def send_welcome_email(user):
        EmailService.send_email(
            to_email=user.email,
            subject='خوش‌آمدگویی به فروشگاه',
            template_name='emails/welcome.html',
            context={'user': user},
        )

    @staticmethod
    def send_order_confirmation(user, order):
        EmailService.send_email(
            to_email=user.email,
            subject=f'تایید سفارش #{order.id}',
            template_name='emails/order_confirmation.html',
            context={'user': user, 'order': order},
        )
