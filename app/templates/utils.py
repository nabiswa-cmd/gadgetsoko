from django.core.mail import send_mail
from django.conf import settings

def send_order_email(order):
    subject = f"Order Confirmation - #{order.id}"

    message = f"""
Hello {order.customer_name},

Your order has been successfully placed.

Order ID: {order.id}
Amount Paid: {order.total_amount}
Date: {order.created_at}
Status: {order.status}

Thank you for shopping with us.
"""

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [order.customer_email],
        fail_silently=False,
    )