from django.db import transaction
from django.utils import timezone
from .models import Order


class OrderWorkflow:
    @staticmethod
    def draft_to_planned(order):
        with transaction.atomic():
            order.status = 'planned'
            order.save()

    @staticmethod
    def planned_to_producing(order):
        with transaction.atomic():
            order.status = 'producing'
            order.save()

    @staticmethod
    def producing_to_completed(order):
        with transaction.atomic():
            order.status = 'completed'
            order.save()

    @staticmethod
    def mark_paid(order):
        with transaction.atomic():
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()

    @staticmethod
    def mark_shipped(order, tracking_code=''):
        with transaction.atomic():
            order.status = 'shipped'
            order.tracking_code = tracking_code
            order.save()

    @staticmethod
    def mark_delivered(order):
        with transaction.atomic():
            order.status = 'delivered'
            order.save()

    @staticmethod
    def cancel_order(order):
        with transaction.atomic():
            order.status = 'cancelled'
            order.save()
