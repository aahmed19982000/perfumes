from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Order Confirmation - #{order.order_number}'
        
        # Render HTML template
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'customer': order.customer
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Confirmation email sent for order {order.order_number}"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return str(e)

@shared_task
def send_order_status_update_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f'Update on your Order #{order.order_number}'
        
        # Render HTML template
        html_message = render_to_string('emails/status_update.html', {
            'order': order,
            'status_display': order.get_status_display()
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Status update email sent for order {order.order_number}"
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return str(e)
